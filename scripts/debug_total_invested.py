#!/usr/bin/env python3
"""
Debug: Total Invested Amount Calculation
Verify the correct calculation for Ayush Investor
"""

print('🔍 AYUSH INVESTOR - TOTAL INVESTED CALCULATION')
print('=' * 60)

# Ayush Investor (user_003) transactions from data_models.py
transactions = [
    {'symbol': 'AAPL', 'type': 'Buy', 'quantity': 10, 'price': 200.0, 'date': '2025-01-10'},
    {'symbol': 'TSLA', 'type': 'Buy', 'quantity': 5, 'price': 240.0, 'date': '2025-01-25'},
    {'symbol': 'INFY', 'type': 'Buy', 'quantity': 10, 'price': 17.8, 'date': '2025-02-15'},
    {'symbol': 'AAPL', 'type': 'Sell', 'quantity': 5, 'price': 210.0, 'date': '2025-03-10'},
]

print('📊 TRANSACTION BREAKDOWN:')
print()

total_buy_amount = 0
total_sell_amount = 0
total_buy_fees = 0
total_sell_fees = 0

for txn in transactions:
    amount = txn['quantity'] * txn['price']
    fees = round(amount * 0.001, 2)  # 0.1% fee
    
    print(f'{txn["date"]}: {txn["type"]:4} {txn["quantity"]:2} {txn["symbol"]:4} @ ${txn["price"]:6.2f} = ${amount:8.2f} (fees: ${fees:5.2f})')
    
    if txn['type'] == 'Buy':
        total_buy_amount += amount
        total_buy_fees += fees
    else:  # Sell
        total_sell_amount += amount
        total_sell_fees += fees

print()
print('=' * 60)
print('💰 SUMMARY:')
print(f'Total Buy Transactions:  ${total_buy_amount:8.2f}')
print(f'Total Buy Fees:          ${total_buy_fees:8.2f}')
print(f'Total Invested (Buy+Fees): ${total_buy_amount + total_buy_fees:8.2f}')
print()
print(f'Total Sell Transactions: ${total_sell_amount:8.2f}')
print(f'Total Sell Fees:         ${total_sell_fees:8.2f}')
print(f'Total Received (Sell-Fees): ${total_sell_amount - total_sell_fees:8.2f}')
print()
print(f'NET AMOUNT INVESTED:     ${(total_buy_amount + total_buy_fees) - (total_sell_amount - total_sell_fees):8.2f}')

print()
print('🤔 COMPARISON WITH UI:')
ui_total = 3378.00
calculated_total = total_buy_amount + total_buy_fees
print(f'UI Shows:                ${ui_total:8.2f}')
print(f'Should Show:             ${calculated_total:8.2f}')
print(f'Difference:              ${ui_total - calculated_total:8.2f}')

if abs(ui_total - calculated_total) > 1:
    print()
    print('❌ MISMATCH DETECTED!')
    print('The UI is showing a different amount than expected.')
    print('Possible causes:')
    print('1. Old transaction data cached in system')
    print('2. Different fee calculation method')
    print('3. Additional transactions not visible here')
    print('4. Bug in total invested calculation logic')
else:
    print()
    print('✅ Calculation matches!')

print()
print('📝 BREAKDOWN BY STOCK:')
buy_amounts = {}
for txn in transactions:
    if txn['type'] == 'Buy':
        symbol = txn['symbol']
        amount = txn['quantity'] * txn['price']
        fees = round(amount * 0.001, 2)
        total_with_fees = amount + fees
        
        if symbol not in buy_amounts:
            buy_amounts[symbol] = {'amount': 0, 'fees': 0, 'total': 0}
        
        buy_amounts[symbol]['amount'] += amount
        buy_amounts[symbol]['fees'] += fees
        buy_amounts[symbol]['total'] += total_with_fees

for symbol, data in buy_amounts.items():
    print(f'{symbol}: ${data["amount"]:7.2f} + ${data["fees"]:5.2f} fees = ${data["total"]:7.2f}')
