run:
	jupyter-nbconvert --debug --execute --ExecutePreprocessor.timeout=21600 main.ipynb

pdf:
	jupyter nbconvert graph.ipynb --to pdf

markdown:
	mkdir -p graph.md
	jupyter nbconvert graph.ipynb --to markdown --output-dir graph.md

python:
	jupyter nbconvert order.ipynb --to python

init-trade-mxc:
	@sudo cp trade-mxc.service /etc/systemd/system/
	@sudo systemctl daemon-reload
	@sudo systemctl enable trade-mxc.service

del-trade-mxc:
	@sudo rm /etc/systemd/system/trade-mxc.service
	@sudo systemctl daemon-reload
	@sudo systemctl disable trade-mxc.service

restart-trade-mxc:
	@sudo systemctl restart trade-mxc.service

stop-trade-mxc:
	@sudo systemctl stop trade-mxc.service

init-trade-binance:
	@sudo cp trade-binance.service /etc/systemd/system/
	@sudo systemctl daemon-reload
	@sudo systemctl enable trade-binance.service

del-trade-binance:
	@sudo rm /etc/systemd/system/trade-binance.service
	@sudo systemctl daemon-reload
	@sudo systemctl disable trade-binance.service

restart-trade-binance:
	@sudo systemctl restart trade-binance.service

stop-trade-binance:
	@sudo systemctl stop trade-binance.service

init-trade-bitbank:
	@sudo cp trade-bitbank.service /etc/systemd/system/
	@sudo systemctl daemon-reload
	@sudo systemctl enable trade-bitbank.service

del-trade-bitbank:
	@sudo rm /etc/systemd/system/trade-bitbank.service
	@sudo systemctl daemon-reload
	@sudo systemctl disable trade-bitbank.service

restart-trade-bitbank:
	@sudo systemctl restart trade-bitbank.service

stop-trade-bitbank:
	@sudo systemctl stop trade-bitbank.service
