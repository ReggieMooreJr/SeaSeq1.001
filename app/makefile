.PHONY: cli api both down reset

cli:
	@echo "🚀 Running SEA-SEQ CLI..."
	./run-sea-seq.sh cli

api:
	@echo "🚀 Running SEA-SEQ API..."
	./run-sea-seq.sh api

both:
	@echo "🚀 Running SEA-SEQ CLI + API..."
	./run-sea-seq.sh both

down:
	@echo "🛑 Stopping and cleaning containers..."
	./run-sea-seq.sh down

reset:
	@echo "🔄 Full reset: prune system, rebuild, run both..."
	./reset-sea-seq.sh both
