import uuid
import json
import re
from typing import Dict, Any, Optional
from openai import OpenAI
import os

# Support running both as a package and as a standalone script
try:
    from .constants import GPT_CONFIGS  # type: ignore
    from .prompts import GPT_PROMPTS  # type: ignore
except ImportError:  # pragma: no cover - fallback for direct script execution
    from constants import GPT_CONFIGS  # type: ignore
    from prompts import GPT_PROMPTS  # type: ignore

class GPTService:
    def __init__(self):
        # Initialize OpenAI client with explicit httpx configuration
        try:
            import httpx
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                http_client=httpx.Client(
                    timeout=httpx.Timeout(30.0, connect=10.0),
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                )
            )
        except Exception as e:
            # Fallback to basic initialization if httpx configuration fails
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def select_gpt(self, gpt_type: str) -> Dict[str, Any]:
        """Select which GPT to use for the session"""
        session_id = str(uuid.uuid4())
        gpt_config = GPT_CONFIGS.get(gpt_type, GPT_CONFIGS["offer_clarifier"])
        
        self.sessions[session_id] = {
            "gpt_type": gpt_type,
            "messages": [{"role": "system", "content": GPT_PROMPTS.get(gpt_type, GPT_PROMPTS["offer_clarifier"])}],
            "fields": {field: None for field in gpt_config["fields"]},
            "current_question": 0  # Track which question we're on
        }
        
        # Get greeting based on GPT type
        greeting = self._get_greeting(gpt_type)
        
        return {
            "session_id": session_id,
            "gpt_type": gpt_type,
            "greeting": greeting
        }
    
    def chat(self, req) -> Dict[str, Any]:
        """Handle chat messages with the selected GPT"""
        session_id = req.session_id or str(uuid.uuid4())
        gpt_type = req.gpt_type or "offer_clarifier"
        
        # Initialize new session if doesn't exist
        if session_id not in self.sessions:
            gpt_config = GPT_CONFIGS.get(gpt_type, GPT_CONFIGS["offer_clarifier"])
            self.sessions[session_id] = {
                "gpt_type": gpt_type,
                "messages": [{"role": "system", "content": GPT_PROMPTS.get(gpt_type, GPT_PROMPTS["offer_clarifier"])}],
                "fields": {field: None for field in gpt_config["fields"]},
                "current_question": 0
            }
        
        session = self.sessions[session_id]
        user_message = req.message.strip()
        
        # Add user message to conversation
        session["messages"].append({"role": "user", "content": user_message})
        
        # Check if user requested summary
        if self._wants_summary(user_message):
            return self._handle_summary_request(session_id, session)
        
        # Check if user wants to proceed
        if self._wants_to_proceed(user_message):
            return self._handle_proceed_request(session_id, session)
        
        # Generate AI response
        try:
            chat_resp = self.client.chat.completions.create(
                model="gpt-4",
                messages=session["messages"],
                temperature=0.8
            )
            reply = chat_resp.choices[0].message.content
            session["messages"].append({"role": "assistant", "content": reply})
            
            # Extract structured data from conversation
            self._extract_fields(session)
            
            # Check if complete
            is_complete = all(session["fields"].values())
            if is_complete:
                final_report = self._generate_final_report(session["fields"], session["gpt_type"])
                return {
                    "session_id": session_id,
                    "reply": final_report,
                    "fields": session["fields"],
                    "gpt_type": session["gpt_type"],
                    "is_complete": True
                }
            
            return {
                "session_id": session_id,
                "reply": reply,
                "fields": session["fields"],
                "gpt_type": session["gpt_type"],
                "is_complete": False
            }
            
        except Exception as e:
            return {
                "session_id": session_id,
                "reply": f"I encountered an error: {str(e)}. Please try again.",
                "fields": session["fields"],
                "gpt_type": session["gpt_type"],
                "is_complete": False
            }
    
    def reset_session(self, session_id: str) -> Dict[str, str]:
        """Reset a conversation session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        return {"status": "reset", "session_id": session_id}
    
    def get_combined_summary(self, session_ids: list) -> Dict[str, Any]:
        """Generate a combined summary from multiple GPT sessions"""
        combined_data = self._collect_session_data(session_ids)
        
        if not combined_data["sessions_found"]:
            return {"error": "No valid sessions found"}
        
        combined_report = self._generate_combined_report(combined_data)
        
        return {
            "combined_report": combined_report,
            "sessions_data": combined_data["sessions_found"]
        }
    
    def get_session_count(self) -> int:
        """Get the number of active sessions"""
        return len(self.sessions)
    
    def _get_greeting(self, gpt_type: str) -> str:
        """Get the initial greeting for a GPT type"""
        greetings = {
            "offer_clarifier": """🎯 **Offer Clarifier GPT**

Hi! I'm here to help you clearly define your offer so all future GPTs can build the perfect campaign around it.

Let's start with the first question: **What is your product, service, or offer called?**

I'll ask you 9 key questions one at a time to get a complete picture of your offer.""",
            
            "avatar_creator": """👤 **Avatar Creator & Empathy Map GPT**

Hi! I'm here to help you build a complete customer avatar using the DigitalMarketer framework. I'll guide you through this step-by-step, asking one question at a time.

Let's start with the basics: **Who is your ideal customer?** Think about someone you've helped before or someone you'd love to work with. For example: "busy moms," "real estate agents," "gym owners," or "freelance designers." If you're not sure, describe a great customer you've worked with in the past.""",
            
            "before_state_research": """🔍 **Before State Research GPT**

Hi! I'm here to help you uncover and enrich your customer avatar's emotional, psychological, and situational "before" state using the DigitalMarketer framework.

To get started, please **provide a copy of your customer avatar**. This can be from the Avatar Creator GPT or any existing customer profile you have. I'll help you dive deep into their struggles, frustrations, and the "evil" they're facing before they find your solution.""",
            
            "after_state_research": """🌞 **After State Research GPT**

Hi! I'm here to help you create compelling and emotionally rich "after" states for your customer avatar using the DigitalMarketer framework.

To get started, please **provide your updated avatar with the before state**. I'll help you craft an inspiring transformation narrative that shows what life looks like after they've achieved success with your solution. This will create powerful marketing messages that motivate action!""",
            
            "avatar_validator": """✅ **Avatar Validator GPT**

Hi! I'm here to analyze your completed customer avatar profile and identify any vague data, missing areas, or conflicting information using the DigitalMarketer framework.

To get started, please **provide your completed customer avatar profile** (including before and after states if available). I'll systematically review each section and provide specific suggestions for improvement, plus deliver a final validated avatar that's ready for marketing use!""",
            
            "trigger_gpt": """🚀 **Trigger GPT**

Hi! I'm here to help you identify what life and business events trigger your ideal customers to start seeking solutions like yours.

To get started, please **provide your customer avatar** (especially focusing on their before state and frustrations). I'll analyze their profile and identify specific trigger moments that shift them from "I'm fine" to "I need to solve this NOW!" - plus suggest content ideas and entry point offers for each trigger!""",
            
            "epo_builder": """🎯 **EPO Builder GPT**

Hi! I'm here to help you generate compelling Entry Point Offers (lead magnets, tripwires, low-cost offers) that connect with your customer avatar's pain points and triggering events.

To get started, please **provide your customer avatar, triggers, and headlines from your previous GPT sessions**. I'll analyze them and create 3 EPO options for each trigger, including implementation details and micro-commitment strategies that smoothly move prospects into your Customer Value Journey!""",
            
            "scamper_synthesizer": """🔄 **SCAMPER Synthesizer**

Hi! I'm here to help you take your existing offer, campaign, or strategy and make it more original, creative, and strategically different using the SCAMPER framework.

To get started, please **provide your existing concept/offer details, customer avatar, and which Customer Value Journey stage you want to focus on**. I'll use the 7 SCAMPER lenses (Substitute, Combine, Adapt, Modify, Put to Another Use, Eliminate, Reverse) to generate innovative variations that increase customers, purchase value, and frequency!""",
            
            "wildcard_idea_bot": """🃏 **Wildcard Idea Bot**

Hi! I'm here to inject bold, unexpected, and creative marketing ideas into your campaigns to prevent them from being predictable, generic, or boring.

To get started, please **provide your product/service description, customer avatar information, and any early-stage campaign ideas or messaging hooks you've developed**. I'll challenge assumptions and introduce 3-5 wildcard ideas that push boundaries, include humor or emotion, and surprise your audience while keeping your business goals in mind!""",
            
            "concept_crafter": """🔍 **Concept Crafter Bot**

Hi! I'm here to transform your business offerings into compelling positioning, hooks, headlines, and messaging concepts that resonate emotionally with your target audience and differentiate you from competitors.

To get started, please **provide your product/service description, customer avatar information, and your business goals**. I'll create powerful main hooks, positioning one-liners, value propositions, taglines, and voice/tone recommendations that convert prospects into customers!""",
            
            "hook_headline_gpt": """🔥 **Hook & Headline GPT**

Hi! I'm an elite-level marketing copywriter here to transform your customer insights into scroll-stopping, emotion-driven messaging that gets clicks, opens, and conversions.

To get started, please **provide your Avatar document (with pain, desire, before/after states), Concept Crafter output (with messaging themes), and Trigger Events**. I'll create magnetic hooks and headlines mapped to Customer Value Journey stages that make people stop and say: "They're talking about me!" """,
            
            "campaign_concept_generator": """🌟 **Campaign Concept Generator GPT**

Hi! I'm here to use everything upstream to generate 2-3 compelling campaign ideas with clear messages, paths to action, and mapped-out customer journeys.

To get started, please **provide your Avatar (validated), TriggerGPT output, Concept Crafter output (3 concept themes), Hooks & Headlines output, and Funnel Strategy map**. I'll create complete campaign concepts that help you visualize exactly how each campaign could work!""",
            
            "idea_injection_bot": """💡 **Idea Injection Bot**

Hi! I'm here to capture your lightning-in-a-bottle moments - those brilliant ideas, insights, and creative "aha!" moments that pop up during or after using EUREKA.

Got an idea you want to drop in? Share **any thought, tweak, or insight** and I'll tag it properly so other GPTs can use it later. Every creative spark matters!"""
        }
        
        return greetings.get(gpt_type, greetings["offer_clarifier"])
    
    def _wants_summary(self, message: str) -> bool:
        """Check if user wants a summary"""
        summary_keywords = ["summary", "summarize", "can you sum up", "give me a recap", "show me what we have", "generate report", "create report"]
        return any(re.search(rf"\b{k}\b", message.lower()) for k in summary_keywords)
    
    def _wants_to_proceed(self, message: str) -> bool:
        """Check if user wants to proceed"""
        proceed_keywords = ["okay", "yes", "proceed", "continue", "let's continue", "next question", "go ahead"]
        return any(re.search(rf"\b{k}\b", message.lower()) for k in proceed_keywords)
    
    def _handle_summary_request(self, session_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """Handle summary request"""
        missing_fields = [f for f, v in session["fields"].items() if not v]
        
        if missing_fields:
            summary_text = f"""Here's what we have so far:
            
{json.dumps({k: v for k, v in session["fields"].items() if v}, indent=2)}

We still need to cover: {', '.join(missing_fields)}

Would you like to continue with the remaining questions?"""
        else:
            summary_text = self._generate_final_report(session["fields"], session["gpt_type"])
        
        return {
            "session_id": session_id, 
            "reply": summary_text,
            "fields": session["fields"],
            "is_complete": all(session["fields"].values())
        }
    
    def _handle_proceed_request(self, session_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """Handle proceed request"""
        missing_fields = [f for f, v in session["fields"].items() if not v]
        
        if missing_fields:
            # Add context to help the AI continue
            session["messages"].append({"role": "system", "content": f"User wants to proceed. Missing fields: {missing_fields}. Ask the next logical question naturally."})
            
            # Get AI response for continuing
            continue_resp = self.client.chat.completions.create(
                model="gpt-4",
                messages=session["messages"],
                temperature=0.8
            )
            continue_reply = continue_resp.choices[0].message.content
            session["messages"].append({"role": "assistant", "content": continue_reply})
            
            return {
                "session_id": session_id,
                "reply": continue_reply,
                "fields": session["fields"],
                "is_complete": False
            }
        
        return {
            "session_id": session_id,
            "reply": "Great! We've covered all the key areas. Would you like me to generate a summary report?",
            "fields": session["fields"],
            "is_complete": True
        }
    
    def _extract_fields(self, session: Dict[str, Any]):
        """Extract structured data from conversation using OpenAI"""
        try:
            # Create extraction prompt based on GPT type
            if session["gpt_type"] == "offer_clarifier":
                extraction_prompt = """Extract the following fields from the conversation below. Return ONLY valid JSON with null for missing fields:

{
  "product_name": "The name of the product/service/offer",
  "core_transformation": "The main outcome or transformation customers get", 
  "features": ["Key features or deliverables as array"],
  "delivery_method": "How it's delivered (live, digital, coaching, etc.)",
  "format": "What format it's in (course, membership, service, SaaS, etc.)",
  "pricing": "Price or pricing model",
  "unique_value": "What makes it different/unique (USP)",
  "target_audience": "Who it's for/ideal customer",
  "problems_solved": ["Problems it solves as array"]
}

Conversation:
"""
            elif session["gpt_type"] == "avatar_creator":
                extraction_prompt = """Extract the following fields from the conversation below. Return ONLY valid JSON with null for missing fields:

{
  "customer_segment": "Who is their ideal customer",
  "avatar_name": "The name given to the avatar",
  "demographics": "Age, job, income, location, family, lifestyle details",
  "frustrations_fears": "Problems they face, what keeps them up at night",
  "wants_aspirations": "Dreams, goals, what they're working toward, values",
  "purchase_drivers": "What makes them say yes, what they value most",
  "objections": "What might stop them from buying, concerns, hesitations",
  "decision_making": "How they make decisions, who influences them",
  "before_state": "Life before the solution, how they feel, struggles",
  "after_state": "Life after using the solution, improvements, new feelings",
  "emotional_shift": "Emotional transformation from negative to positive"
}

Conversation:
"""
            elif session["gpt_type"] == "before_state_research":
                extraction_prompt = """Extract the following fields from the conversation below. Return ONLY valid JSON with null for missing fields:

{
  "avatar_input": "The original customer avatar data provided",
  "what_they_have": "What unwanted or frustrating things they have in their life right now",
  "how_they_feel": "How they feel emotionally - frustrated, overwhelmed, lost, anxious, etc.",
  "average_day": "What their typical day looks like and where struggles show up",
  "status": "How they feel about themselves or how others see them",
  "evil_they_face": "What they think is the cause of the problem or root cause they're fighting",
  "research_communities": "Online communities where people talk about this situation",
  "emotional_patterns": "Patterns in emotions and struggles found in research",
  "before_state_narrative": "Complete before state story in narrative format",
  "empathy_map": "Empathy map summary of their before state"
}

Conversation:
"""
            else:
                # Generic extraction for other GPT types
                extraction_prompt = """Extract relevant information from the conversation below. Return ONLY valid JSON with the fields that are mentioned:

{
  "extracted_data": "Any relevant information found in the conversation"
}

Conversation:
"""
            
            # Get last few messages for context
            recent_messages = session["messages"][-6:]  # Last 6 messages
            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
            
            extraction_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strict JSON data extractor. Extract only the fields mentioned in the conversation. Be conservative - only extract if clearly stated."},
                    {"role": "user", "content": extraction_prompt + conversation_text}
                ],
                temperature=0
            )
            
            try:
                extracted_data = json.loads(extraction_response.choices[0].message.content)
                # Update session fields with extracted data
                for key in session["fields"]:
                    if extracted_data.get(key) and not session["fields"][key]:
                        session["fields"][key] = extracted_data[key]
            except json.JSONDecodeError:
                pass  # Continue without extraction if JSON parsing fails
                
        except Exception as e:
            # If extraction fails, continue without it
            pass
    
    def _generate_final_report(self, fields_data: Dict[str, Any], gpt_type: str) -> str:
        """Generate final report based on GPT type"""
        if gpt_type == "offer_clarifier":
            return self._generate_offer_clarifier_report(fields_data)
        elif gpt_type == "avatar_creator":
            return self._generate_avatar_creator_report(fields_data)
        elif gpt_type == "before_state_research":
            return self._generate_before_state_research_report(fields_data)
        else:
            return f"Final report for {gpt_type} - Data collected: {json.dumps(fields_data, indent=2)}"
    
    def _generate_offer_clarifier_report(self, fields_data: Dict[str, Any]) -> str:
        """Generate the specific Offer Clarifier report format"""
        
        # Format features
        features_text = ""
        if fields_data.get("features"):
            if isinstance(fields_data["features"], list):
                for feature in fields_data["features"]:
                    features_text += f"* {feature}\n"
            else:
                features_text = f"* {fields_data['features']}\n"
        
        # Format problems solved
        problems_text = ""
        if fields_data.get("problems_solved"):
            if isinstance(fields_data["problems_solved"], list):
                for problem in fields_data["problems_solved"]:
                    problems_text += f"* {problem}\n"
            else:
                problems_text = f"* {fields_data['problems_solved']}\n"
        
        # Create JSON for downstream GPTs
        json_output = {
            "title": fields_data.get("product_name", ""),
            "coreOutcome": fields_data.get("core_transformation", ""),
            "features": fields_data.get("features", []) if isinstance(fields_data.get("features"), list) else [fields_data.get("features", "")],
            "delivery": fields_data.get("delivery_method", ""),
            "format": fields_data.get("format", ""),
            "pricePoint": fields_data.get("pricing", ""),
            "USP": fields_data.get("unique_value", ""),
            "targetAudience": fields_data.get("target_audience", ""),
            "problemsSolved": fields_data.get("problems_solved", []) if isinstance(fields_data.get("problems_solved"), list) else [fields_data.get("problems_solved", "")]
        }
        
        report = f"""#### ✅ OFFER CLARIFIER – OUTCOME SUMMARY REPORT

**Here's a full breakdown of your offer based on your answers:**

**💼 Offer Name**
{fields_data.get('product_name', '[Not specified]')}

**🌟 Core Transformation / Outcome**
{fields_data.get('core_transformation', '[Not specified]')}

**📦 Key Features (list as many features as you identify)**
{features_text.rstrip() if features_text else '* [Not specified]'}

**🚚 Delivery Method**
{fields_data.get('delivery_method', '[Not specified]')}

**🧩 Format**
{fields_data.get('format', '[Not specified]')}

**💰 Price & Payment**
{fields_data.get('pricing', '[Not specified]')}

**🧠 Unique Selling Proposition (USP)**
{fields_data.get('unique_value', '[Not specified]')}

**🎯 Target Audience**
{fields_data.get('target_audience', '[Not specified]')}

**🔥 Problems Solved (list as many problems it solves as you can come up with)**
{problems_text.rstrip() if problems_text else '* [Not specified]'}

**➡️ Does this look good?**
"Yes" to proceed — or tell me what to change.

---

#### 🧾 JSON OUTPUT (For downstream GPTs)
```json
{json.dumps(json_output, indent=2)}
```"""
        
        return report
    
    def _generate_avatar_creator_report(self, fields_data: Dict[str, Any]) -> str:
        """Generate the specific Avatar Creator report format"""
        
        # Format customer segment
        customer_segment_text = fields_data.get("customer_segment", "[Not specified]")
        
        # Format avatar name
        avatar_name_text = fields_data.get("avatar_name", "[Not specified]")
        
        # Format demographics
        demographics_text = ""
        if fields_data.get("demographics"):
            if isinstance(fields_data["demographics"], list):
                for item in fields_data["demographics"]:
                    demographics_text += f"* {item}\n"
            else:
                demographics_text = f"* {fields_data['demographics']}\n"
        
        # Format frustrations/fears
        frustrations_fears_text = ""
        if fields_data.get("frustrations_fears"):
            if isinstance(fields_data["frustrations_fears"], list):
                for item in fields_data["frustrations_fears"]:
                    frustrations_fears_text += f"* {item}\n"
            else:
                frustrations_fears_text = f"* {fields_data['frustrations_fears']}\n"
        
        # Format wants/aspirations
        wants_aspirations_text = ""
        if fields_data.get("wants_aspirations"):
            if isinstance(fields_data["wants_aspirations"], list):
                for item in fields_data["wants_aspirations"]:
                    wants_aspirations_text += f"* {item}\n"
            else:
                wants_aspirations_text = f"* {fields_data['wants_aspirations']}\n"
        
        # Format purchase drivers
        purchase_drivers_text = ""
        if fields_data.get("purchase_drivers"):
            if isinstance(fields_data["purchase_drivers"], list):
                for item in fields_data["purchase_drivers"]:
                    purchase_drivers_text += f"* {item}\n"
            else:
                purchase_drivers_text = f"* {fields_data['purchase_drivers']}\n"
        
        # Format objections
        objections_text = ""
        if fields_data.get("objections"):
            if isinstance(fields_data["objections"], list):
                for item in fields_data["objections"]:
                    objections_text += f"* {item}\n"
            else:
                objections_text = f"* {fields_data['objections']}\n"
        
        # Format decision making
        decision_making_text = ""
        if fields_data.get("decision_making"):
            if isinstance(fields_data["decision_making"], list):
                for item in fields_data["decision_making"]:
                    decision_making_text += f"* {item}\n"
            else:
                decision_making_text = f"* {fields_data['decision_making']}\n"
        
        # Format before state
        before_state_text = ""
        if fields_data.get("before_state"):
            if isinstance(fields_data["before_state"], list):
                for item in fields_data["before_state"]:
                    before_state_text += f"* {item}\n"
            else:
                before_state_text = f"* {fields_data['before_state']}\n"
        
        # Format after state
        after_state_text = ""
        if fields_data.get("after_state"):
            if isinstance(fields_data["after_state"], list):
                for item in fields_data["after_state"]:
                    after_state_text += f"* {item}\n"
            else:
                after_state_text = f"* {fields_data['after_state']}\n"
        
        # Format emotional shift
        emotional_shift_text = ""
        if fields_data.get("emotional_shift"):
            if isinstance(fields_data["emotional_shift"], list):
                for item in fields_data["emotional_shift"]:
                    emotional_shift_text += f"* {item}\n"
            else:
                emotional_shift_text = f"* {fields_data['emotional_shift']}\n"
        
        # Create JSON for downstream GPTs
        json_output = {
            "customerSegment": customer_segment_text,
            "avatarName": avatar_name_text,
            "demographics": fields_data.get("demographics", []),
            "frustrationsFears": fields_data.get("frustrations_fears", []),
            "wantsAspirations": fields_data.get("wants_aspirations", []),
            "purchaseDrivers": fields_data.get("purchase_drivers", []),
            "objections": fields_data.get("objections", []),
            "decisionMaking": fields_data.get("decision_making", []),
            "beforeState": fields_data.get("before_state", []),
            "afterState": fields_data.get("after_state", []),
            "emotionalShift": fields_data.get("emotional_shift", [])
        }
        
        report = f"""#### 📸 AVATAR CREATOR – COMPLETE CUSTOMER AVATAR REPORT

**Here's a complete breakdown of your customer avatar based on your answers:**

**👤 Avatar Name**
{avatar_name_text}

**👥 Customer Segment**
{customer_segment_text}

**🧠 Demographics**
{demographics_text.rstrip() if demographics_text else '* [Not specified]'}

**💔 Frustrations & Fears**
{frustrations_fears_text.rstrip() if frustrations_fears_text else '* [Not specified]'}

**💪 Wants & Aspirations**
{wants_aspirations_text.rstrip() if wants_aspirations_text else '* [Not specified]'}

**💰 Purchase Drivers**
{purchase_drivers_text.rstrip() if purchase_drivers_text else '* [Not specified]'}

**🤔 Objections**
{objections_text.rstrip() if objections_text else '* [Not specified]'}

**🧠 Decision Making**
{decision_making_text.rstrip() if decision_making_text else '* [Not specified]'}

**👥 Before State**
{before_state_text.rstrip() if before_state_text else '* [Not specified]'}

**🌞 After State**
{after_state_text.rstrip() if after_state_text else '* [Not specified]'}

**💫 Emotional Shift**
{emotional_shift_text.rstrip() if emotional_shift_text else '* [Not specified]'}

---

#### 🧾 JSON OUTPUT (For downstream GPTs)
```json
{json.dumps(json_output, indent=2)}
```"""
        
        return report
    
    def _generate_before_state_research_report(self, fields_data: Dict[str, Any]) -> str:
        """Generate the specific Before State Research report format"""
        
        # Format avatar input
        avatar_input_text = ""
        if fields_data.get("avatar_input"):
            if isinstance(fields_data["avatar_input"], list):
                for item in fields_data["avatar_input"]:
                    avatar_input_text += f"* {item}\n"
            else:
                avatar_input_text = f"* {fields_data['avatar_input']}\n"
        
        # Format what they have
        what_they_have_text = ""
        if fields_data.get("what_they_have"):
            if isinstance(fields_data["what_they_have"], list):
                for item in fields_data["what_they_have"]:
                    what_they_have_text += f"* {item}\n"
            else:
                what_they_have_text = f"* {fields_data['what_they_have']}\n"
        
        # Format how they feel
        how_they_feel_text = ""
        if fields_data.get("how_they_feel"):
            if isinstance(fields_data["how_they_feel"], list):
                for item in fields_data["how_they_feel"]:
                    how_they_feel_text += f"* {item}\n"
            else:
                how_they_feel_text = f"* {fields_data['how_they_feel']}\n"
        
        # Format average day
        average_day_text = ""
        if fields_data.get("average_day"):
            if isinstance(fields_data["average_day"], list):
                for item in fields_data["average_day"]:
                    average_day_text += f"* {item}\n"
            else:
                average_day_text = f"* {fields_data['average_day']}\n"
        
        # Format status
        status_text = ""
        if fields_data.get("status"):
            if isinstance(fields_data["status"], list):
                for item in fields_data["status"]:
                    status_text += f"* {item}\n"
            else:
                status_text = f"* {fields_data['status']}\n"
        
        # Format evil they face
        evil_they_face_text = ""
        if fields_data.get("evil_they_face"):
            if isinstance(fields_data["evil_they_face"], list):
                for item in fields_data["evil_they_face"]:
                    evil_they_face_text += f"* {item}\n"
            else:
                evil_they_face_text = f"* {fields_data['evil_they_face']}\n"
        
        # Format research communities
        research_communities_text = ""
        if fields_data.get("research_communities"):
            if isinstance(fields_data["research_communities"], list):
                for item in fields_data["research_communities"]:
                    research_communities_text += f"* {item}\n"
            else:
                research_communities_text = f"* {fields_data['research_communities']}\n"
        
        # Format emotional patterns
        emotional_patterns_text = ""
        if fields_data.get("emotional_patterns"):
            if isinstance(fields_data["emotional_patterns"], list):
                for item in fields_data["emotional_patterns"]:
                    emotional_patterns_text += f"* {item}\n"
            else:
                emotional_patterns_text = f"* {fields_data['emotional_patterns']}\n"
        
        # Format before state narrative
        before_state_narrative_text = ""
        if fields_data.get("before_state_narrative"):
            if isinstance(fields_data["before_state_narrative"], list):
                for item in fields_data["before_state_narrative"]:
                    before_state_narrative_text += f"* {item}\n"
            else:
                before_state_narrative_text = f"* {fields_data['before_state_narrative']}\n"
        
        # Format empathy map
        empathy_map_text = ""
        if fields_data.get("empathy_map"):
            if isinstance(fields_data["empathy_map"], list):
                for item in fields_data["empathy_map"]:
                    empathy_map_text += f"* {item}\n"
            else:
                empathy_map_text = f"* {fields_data['empathy_map']}\n"
        
        # Create JSON for downstream GPTs
        json_output = {
            "avatarInput": fields_data.get("avatar_input", []),
            "whatTheyHave": fields_data.get("what_they_have", []),
            "howTheyFeel": fields_data.get("how_they_feel", []),
            "averageDay": fields_data.get("average_day", []),
            "status": fields_data.get("status", []),
            "evilTheyFace": fields_data.get("evil_they_face", []),
            "researchCommunities": fields_data.get("research_communities", []),
            "emotionalPatterns": fields_data.get("emotional_patterns", []),
            "beforeStateNarrative": fields_data.get("before_state_narrative", []),
            "empathyMap": fields_data.get("empathy_map", [])
        }
        
        report = f"""#### 🔍 BEFORE STATE RESEARCH – COMPLETE CUSTOMER AVATAR REPORT

**Here's a complete breakdown of your customer avatar's "before" state based on your answers:**

**👥 Avatar Input**
{avatar_input_text.rstrip() if avatar_input_text else '* [Not specified]'}

**💔 What They Have**
{what_they_have_text.rstrip() if what_they_have_text else '* [Not specified]'}

**💔 How They Feel**
{how_they_feel_text.rstrip() if how_they_feel_text else '* [Not specified]'}

**👥 Average Day**
{average_day_text.rstrip() if average_day_text else '* [Not specified]'}

**👥 Status**
{status_text.rstrip() if status_text else '* [Not specified]'}

**💔 Evil They Face**
{evil_they_face_text.rstrip() if evil_they_face_text else '* [Not specified]'}

**🔗 Research Communities**
{research_communities_text.rstrip() if research_communities_text else '* [Not specified]'}

**🧠 Emotional Patterns**
{emotional_patterns_text.rstrip() if emotional_patterns_text else '* [Not specified]'}

**📖 Before State Narrative**
{before_state_narrative_text.rstrip() if before_state_narrative_text else '* [Not specified]'}

**🤔 Empathy Map**
{empathy_map_text.rstrip() if empathy_map_text else '* [Not specified]'}

---

#### 🧾 JSON OUTPUT (For downstream GPTs)
```json
{json.dumps(json_output, indent=2)}
```"""
        
        return report
    
    def _collect_session_data(self, session_ids: list) -> Dict[str, Any]:
        """Collect data from multiple sessions"""
        combined_data = {
            "sessions_found": []
        }
        
        for session_id in session_ids:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                combined_data["sessions_found"].append({
                    "session_id": session_id,
                    "gpt_type": session.get("gpt_type", "offer_clarifier"),
                    "fields": session["fields"]
                })
        
        return combined_data
    
    def _generate_combined_report(self, combined_data: Dict[str, Any]) -> str:
        """Generate combined report from multiple sessions"""
        # This is a simplified version - you can implement the full combined report
        return f"Combined report from {len(combined_data['sessions_found'])} sessions"
