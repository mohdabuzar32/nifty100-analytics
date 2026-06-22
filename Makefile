load:
	python src/etl/loader.py

ratios:
	python src/etl/ratios.py

test:
	pytest tests/ -v

report:
	python src/report/generate.py

dashboard:
	streamlit run src/dashboard/app.py

api:
	uvicorn src.api.main:app --reload

clean:
	rm -f nifty100.db
