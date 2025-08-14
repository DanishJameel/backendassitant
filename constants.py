# Field definitions for all GPT assistants

OFFER_CLARIFIER_FIELDS = [
    "product_name",
    "core_transformation", 
    "features",
    "delivery_method",
    "format",
    "pricing",
    "unique_value",
    "target_audience",
    "problems_solved"
]

AVATAR_CREATOR_FIELDS = [
    "customer_segment",
    "avatar_name",
    "demographics",
    "frustrations_fears",
    "wants_aspirations",
    "purchase_drivers",
    "objections",
    "decision_making",
    "before_state",
    "after_state",
    "emotional_shift"
]

BEFORE_STATE_RESEARCH_FIELDS = [
    "avatar_input",
    "what_they_have",
    "how_they_feel",
    "average_day",
    "status",
    "evil_they_face",
    "research_communities",
    "emotional_patterns",
    "before_state_narrative",
    "empathy_map"
]

AFTER_STATE_RESEARCH_FIELDS = [
    "avatar_input",
    "what_they_have_now",
    "how_they_feel_now",
    "average_day_now",
    "status_now",
    "good_they_do",
    "research_communities",
    "transformation_language",
    "after_state_narrative",
    "success_stories"
]

AVATAR_VALIDATOR_FIELDS = [
    "avatar_profile_input",
    "demographics_analysis",
    "frustrations_analysis",
    "wants_analysis",
    "purchase_drivers_analysis",
    "before_state_analysis",
    "after_state_analysis",
    "logic_conflicts",
    "missing_areas",
    "improvement_suggestions",
    "validated_avatar"
]

TRIGGER_GPT_FIELDS = [
    "avatar_input",
    "internal_triggers",
    "external_triggers", 
    "seasonal_triggers",
    "trigger_moments",
    "emotional_states",
    "content_ideas",
    "entry_point_offers",
    "trigger_narratives",
    "urgency_factors",
    "predictability_ranking"
]

EPO_BUILDER_FIELDS = [
    "avatar_input",
    "triggers_input",
    "headlines_input",
    "offer_type_analysis",
    "gated_content_offers",
    "loss_leader_offers",
    "product_preview_offers",
    "trial_upgrade_offers",
    "velvet_rope_offers",
    "recommended_offers",
    "micro_commitments",
    "implementation_format"
]

SCAMPER_SYNTHESIZER_FIELDS = [
    "existing_concept_input",
    "customer_avatar_input",
    "cvj_stage_focus",
    "substitute_ideas",
    "combine_ideas",
    "adapt_ideas",
    "modify_magnify_ideas",
    "put_to_another_use_ideas",
    "eliminate_ideas",
    "reverse_rearrange_ideas",
    "selected_innovations",
    "implementation_strategy"
]

WILDCARD_IDEA_BOT_FIELDS = [
    "product_service_input",
    "customer_avatar_input",
    "campaign_ideas_input",
    "wildcard_idea_1",
    "wildcard_idea_2",
    "wildcard_idea_3",
    "wildcard_idea_4",
    "wildcard_idea_5",
    "cvj_stage_mapping",
    "audience_considerations",
    "selected_wildcards",
    "implementation_warnings"
]

CONCEPT_CRAFTER_FIELDS = [
    "product_service_input",
    "customer_avatar_input",
    "business_goals_input",
    "main_hook_headline",
    "positioning_one_liners",
    "value_proposition_paragraph",
    "tagline_ideas",
    "voice_tone_recommendations",
    "style_tips",
    "messaging_angles",
    "emotional_triggers",
    "competitive_differentiation"
]

HOOK_HEADLINE_GPT_FIELDS = [
    "avatar_document_input",
    "concept_crafter_input",
    "trigger_events_input",
    "cvj_stage_focus",
    "concept_1_hooks",
    "concept_2_hooks",
    "concept_3_hooks",
    "email_sms_subject_lines",
    "content_angles",
    "pain_vs_aspiration_hooks",
    "cvj_mapped_messaging",
    "selected_hooks_headlines"
]

CAMPAIGN_CONCEPT_GENERATOR_FIELDS = [
    "avatar_input",
    "trigger_gpt_output",
    "concept_crafter_output",
    "hooks_headlines_output",
    "funnel_strategy_map",
    "offer_stack_epos",
    "campaign_1_concept",
    "campaign_2_concept",
    "campaign_3_concept",
    "campaign_titles",
    "core_hooks_emotions",
    "funnel_strategies",
    "selected_campaign"
]

IDEA_INJECTION_BOT_FIELDS = [
    "user_idea_input",
    "idea_description",
    "idea_tags",
    "connection_areas",
    "user_commentary",
    "timestamp",
    "idea_category",
    "implementation_notes",
    "priority_level",
    "related_gpts",
    "stored_ideas",
    "synthesizer_handoff"
]

# GPT Configuration mapping
GPT_CONFIGS = {
    "offer_clarifier": {
        "fields": OFFER_CLARIFIER_FIELDS,
        "name": "Offer Clarifier",
        "description": "Define your product or service clearly through 9 key questions"
    },
    "avatar_creator": {
        "fields": AVATAR_CREATOR_FIELDS,
        "name": "Avatar Creator & Empathy Map",
        "description": "Build a complete customer avatar using the DigitalMarketer framework"
    },
    "before_state_research": {
        "fields": BEFORE_STATE_RESEARCH_FIELDS,
        "name": "Before State Research",
        "description": "Uncover deep emotional and psychological insights about your avatar's struggles"
    },
    "after_state_research": {
        "fields": AFTER_STATE_RESEARCH_FIELDS,
        "name": "After State Research",
        "description": "Create compelling transformation narratives for your avatar's success state"
    },
    "avatar_validator": {
        "fields": AVATAR_VALIDATOR_FIELDS,
        "name": "Avatar Validator",
        "description": "Analyze and improve your customer avatar for marketing readiness"
    },
    "trigger_gpt": {
        "fields": TRIGGER_GPT_FIELDS,
        "name": "Trigger GPT",
        "description": "Identify what events trigger your customers to seek solutions"
    },
    "epo_builder": {
        "fields": EPO_BUILDER_FIELDS,
        "name": "EPO Builder",
        "description": "Generate compelling Entry Point Offers for your customer journey"
    },
    "scamper_synthesizer": {
        "fields": SCAMPER_SYNTHESIZER_FIELDS,
        "name": "SCAMPER Synthesizer",
        "description": "Innovate your existing concepts using the SCAMPER framework"
    },
    "wildcard_idea_bot": {
        "fields": WILDCARD_IDEA_BOT_FIELDS,
        "name": "Wildcard Idea Bot",
        "description": "Inject bold, unexpected creative ideas to break marketing predictability"
    },
    "concept_crafter": {
        "fields": CONCEPT_CRAFTER_FIELDS,
        "name": "Concept Crafter Bot",
        "description": "Transform your offerings into compelling positioning and messaging"
    },
    "hook_headline_gpt": {
        "fields": HOOK_HEADLINE_GPT_FIELDS,
        "name": "Hook & Headline GPT",
        "description": "Generate scroll-stopping, emotion-driven messaging for all platforms"
    },
    "campaign_concept_generator": {
        "fields": CAMPAIGN_CONCEPT_GENERATOR_FIELDS,
        "name": "Campaign Concept Generator",
        "description": "Create complete campaign ideas with mapped customer journeys"
    },
    "idea_injection_bot": {
        "fields": IDEA_INJECTION_BOT_FIELDS,
        "name": "Idea Injection Bot",
        "description": "Capture creative insights and lightning-in-a-bottle moments"
    }
}
