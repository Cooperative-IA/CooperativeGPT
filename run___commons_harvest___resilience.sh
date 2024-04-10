for i in {1..5}; do 
python main.py --substrate="commons_harvest_open" --scenario="" --adversarial_event=True --agents_bio_config="all_coop" --world_context="context_with_definitions" --prompts_source="base_prompts_v1" --llm_model="gpt-3.5" 
done