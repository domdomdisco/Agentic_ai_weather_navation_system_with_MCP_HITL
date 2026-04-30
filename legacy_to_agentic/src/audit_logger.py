class AuditLogger:
    def __init__(self):
        self.total_cost = 0.0
        # Gemini 1.5 Flash Pricing (USD per 1M tokens)
        self.PRICE_INPUT = 0.075 / 1000000
        self.PRICE_OUTPUT = 0.30 / 1000000

    def log_turn_usage(self, turn_number, usage_metadata):
        """Calculates and prints the cost for a single reasoning turn."""
        input_tokens = usage_metadata.prompt_token_count
        output_tokens = usage_metadata.candidates_token_count
        total_tokens = usage_metadata.total_token_count
        
        turn_cost = (input_tokens * self.PRICE_INPUT) + (output_tokens * self.PRICE_OUTPUT)
        self.total_cost += turn_cost
        
        print(f"\n--- 📊 AUDIT LOG (Turn {turn_number}) ---")
        print(f"Tokens:  {total_tokens} (In: {input_tokens}, Out: {output_tokens})")
        print(f"Cost:    ${turn_cost:.6f}")
        print(f"Total:   ${self.total_cost:.6f}")
        print(f"------------------------------------\n")
        
        return turn_cost, self.total_cost
