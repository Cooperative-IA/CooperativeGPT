for i in {1..5}; do 
python main.py --substrate="commons_harvest_open" --scenario="" --adversarial_event=True  --agents_bio_config="no_bio" --world_context="detailed_context" --llm_model="gpt-3.5"
done