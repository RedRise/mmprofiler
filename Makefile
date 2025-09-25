# Install dependencies using Poetry
install:
	poetry install

# Run the Streamlit app (default script: app)
run:
	poetry run streamlit run ./trajectory.py
