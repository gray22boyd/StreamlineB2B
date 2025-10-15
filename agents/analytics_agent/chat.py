#!/usr/bin/env python3
# agents/analytics_agent/chat.py
"""
Interactive chat interface for testing the Analytics Agent
Run this to test the agent before integrating with the frontend
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.analytics_agent.tools import AnalyticsTools
from agents.analytics_agent.schemas import EXAMPLE_QUESTIONS

load_dotenv()


class AnalyticsAgentChat:
    """Interactive chat interface for analytics agent"""
    
    def __init__(self):
        """Initialize the chat interface"""
        print("[INIT] Initializing Analytics Agent...")
        
        try:
            self.analytics = AnalyticsTools()
            print("[OK] Analytics Agent initialized successfully!\n")
        except Exception as e:
            print(f"[ERROR] Failed to initialize agent: {e}")
            sys.exit(1)
    
    def print_banner(self):
        """Print welcome banner"""
        print("=" * 70)
        print("[ANALYTICS] ANALYTICS AGENT - Interactive Chat")
        print("=" * 70)
        print("\nThis agent can answer questions about your retail business data.")
        print("It will generate SQL queries dynamically based on your questions.\n")
        print("Commands:")
        print("  - Type your question naturally")
        print("  - 'stats' - Show quick business statistics")
        print("  - 'top' - Show top selling products")
        print("  - 'customers' - Show customer insights")
        print("  - 'examples' - Show example questions")
        print("  - 'help' - Show this help")
        print("  - 'quit' or 'exit' - Exit the chat")
        print("=" * 70)
        print()
    
    def print_examples(self):
        """Print example questions"""
        print("\n[EXAMPLES] Example Questions You Can Ask:")
        print("-" * 70)
        for i, example in enumerate(EXAMPLE_QUESTIONS[:10], 1):
            print(f"{i:2}. {example}")
        print("-" * 70)
        print()
    
    def format_response(self, result: dict):
        """Format and print the agent's response"""
        print("\n" + "=" * 70)
        
        if not result.get('success', False):
            print("[ERROR] Error:", result.get('error', 'Unknown error'))
            print("=" * 70)
            return
        
        # Print answer
        if 'answer' in result:
            print("[ANALYTICS] Answer:")
            print("-" * 70)
            print(result['answer'])
            print()
        
        # Print SQL query used
        if 'sql_query' in result:
            print("[SQL] SQL Query Used:")
            print("-" * 70)
            print(result['sql_query'])
            print()
        
        # Print row count
        if 'row_count' in result:
            print(f"[STATS] Rows returned: {result['row_count']}")
        
        # Print stats if present
        if 'stats' in result:
            print("[ANALYTICS] Quick Statistics:")
            print("-" * 70)
            stats = result['stats']
            for key, value in stats.items():
                formatted_key = key.replace('_', ' ').title()
                print(f"  {formatted_key}: {value}")
        
        # Print products if present
        if 'top_products' in result:
            print("[TOP] Top Products:")
            print("-" * 70)
            for i, product in enumerate(result['top_products'], 1):
                print(f"\n{i}. {product.get('product_name', 'Unknown')}")
                print(f"   Category: {product.get('category', 'N/A')}")
                print(f"   Brand: {product.get('brand', 'N/A')}")
                print(f"   Revenue: ${product.get('total_revenue', 0):,.2f}")
                print(f"   Units Sold: {product.get('total_units_sold', 0)}")
        
        # Print customer insights if present
        if 'customer_insights' in result:
            print("[CUSTOMERS] Customer Insights:")
            print("-" * 70)
            for insight in result['customer_insights']:
                if 'customer_name' in insight:
                    # Individual customer
                    print(f"\nCustomer: {insight.get('customer_name')}")
                    print(f"Email: {insight.get('email')}")
                    print(f"Loyalty Tier: {insight.get('loyalty_tier')}")
                    print(f"Location: {insight.get('city')}, {insight.get('state')}")
                    print(f"Customer Since: {insight.get('customer_since')}")
                    print(f"Total Orders: {insight.get('total_orders')}")
                    print(f"Lifetime Value: ${insight.get('lifetime_value', 0):,.2f}")
                else:
                    # Segment summary
                    print(f"\n{insight.get('loyalty_tier', 'Unknown')} Tier:")
                    print(f"  Customers: {insight.get('customer_count')}")
                    print(f"  Orders: {insight.get('total_orders')}")
                    print(f"  Avg Order Value: ${insight.get('avg_order_value', 0):,.2f}")
                    print(f"  Total Revenue: ${insight.get('total_revenue', 0):,.2f}")
        
        print("=" * 70)
        print()
    
    def handle_command(self, user_input: str) -> bool:
        """
        Handle user commands
        
        Returns:
            True to continue, False to exit
        """
        command = user_input.strip().lower()
        
        if command in ['quit', 'exit', 'q']:
            return False
        
        elif command == 'help':
            self.print_banner()
            return True
        
        elif command == 'examples':
            self.print_examples()
            return True
        
        elif command == 'stats':
            print("\n[WAIT] Fetching quick statistics...")
            result = self.analytics.get_quick_stats()
            self.format_response(result)
            return True
        
        elif command == 'top':
            print("\n[WAIT] Fetching top products...")
            result = self.analytics.get_top_products(limit=10)
            self.format_response(result)
            return True
        
        elif command == 'customers':
            print("\n[WAIT] Fetching customer insights...")
            result = self.analytics.get_customer_insights()
            self.format_response(result)
            return True
        
        else:
            # Treat as a natural language question
            print("\n[WAIT] Processing your question...")
            print("[AI] Generating SQL query...")
            result = self.analytics.query_database(user_input)
            self.format_response(result)
            return True
    
    def run(self):
        """Run the interactive chat loop"""
        self.print_banner()
        
        print("[TIP] Tip: Try 'examples' to see sample questions or 'stats' for quick overview\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle command/question
                should_continue = self.handle_command(user_input)
                
                if not should_continue:
                    print("\n[BYE] Thanks for using Analytics Agent! Goodbye!")
                    break
            
            except KeyboardInterrupt:
                print("\n\n[BYE] Interrupted. Goodbye!")
                break
            
            except Exception as e:
                print(f"\n[ERROR] Error: {e}")
                print("Please try again or type 'help' for assistance.\n")


def main():
    """Main entry point"""
    # Check for required environment variables
    if not os.getenv('DATABASE_URL'):
        print("[ERROR] Error: DATABASE_URL environment variable not set")
        print("Please add it to your .env file")
        sys.exit(1)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("[ERROR] Error: OPENAI_API_KEY environment variable not set")
        print("Please add it to your .env file")
        sys.exit(1)
    
    # Create and run chat
    chat = AnalyticsAgentChat()
    chat.run()


if __name__ == '__main__':
    main()



