for i in {1..6}; do 
python main.py --substrate="commons_harvest_open" --scenario="" --kind_experiment="adversarial"  --agents_bio_config="all_coop" --world_context="context_with_definitions" --llm_model="gpt-3.5"
done