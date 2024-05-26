from web3 import Web3
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Get environment variables
infura_url = os.getenv('INFURA_URL')
wallet_address = os.getenv('WALLET_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')
router_abi_json = os.getenv('ROUTER_ABI_JSON')
erc20_token_abi_json = os.getenv('ERC20_TOKEN_ABI_JSON')

# Connect to Infura or any other Ethereum node
web3 = Web3(Web3.HTTPProvider(infura_url))

print("wish web3:", web3, "\n")

# Check if connected
print("Is connected:", web3.is_connected())

# Check if connected to the node
if not web3.is_connected():
    print("Failed to connect to the Ethereum node.")
    exit()

#  V2 router contract address and ABI
router_address = '0xD5Dd9341Af9932C2951eB0eE7578f79334fdc8cc'  
router_abi = json.loads(router_abi_json)

# print("Router address:", router_address)
# print("Router ABI:", router_abi)

# Create contract instance
router = web3.eth.contract(address=router_address, abi=router_abi)

print("Router instance created.",router)

# Token details
erc20_token_address = '0xa8e3C7fE1085C4A78EC28d7dc4E6FE86e45Dec65'  
erc20_token_abi = json.loads(erc20_token_abi_json)

# Create contract instance for the ERC20 token
erc20_token = web3.eth.contract(address=erc20_token_address, abi=erc20_token_abi)

print("ERC20 token instance created:", erc20_token)

# Amount of ETH to swap (in Wei)
amount_in_wei = web3.to_wei(0.01, 'ether')

print("Amount in Wei:", amount_in_wei)
print("wallet address:",wallet_address)

# Define the transaction parameters
transaction = {
    'from': wallet_address,
    'value': amount_in_wei,
    'gas': 2000000,
    'gasPrice': web3.to_wei('5', 'gwei'),
    'nonce': web3.eth.get_transaction_count(wallet_address)
}

print("Transaction:", transaction)

# Set the slippage tolerance and deadline for the transaction
slippage_tolerance = 0.5  # 0.5%
deadline = web3.eth.get_block('latest')['timestamp'] + 600  # 10 minutes from the current block timestamp

# Call to the read function
try:
    test = router.functions.WETH().call()
    print("test:", test)
except Exception as e:
    print("Error:", e)


# try:
#     test2 = web3.to_checksum_address(router_address)
#     print("test2:", test2)
# except Exception as e:
#     print("Error:", e)


# Fetch the current exchange rate and calculate the minimum amount of tokens to accept (for slippage tolerance)
try:
    amount_out_min = router.functions.getAmountsOut(amount_in_wei, [web3.to_checksum_address(router_address), erc20_token_address]).call()[1]
    print("Amount out min:", amount_out_min)
except Exception as e:
    print("Error:", e)


# amount_out_min = int(amount_out_min * (1 - slippage_tolerance / 100))

# # Build the transaction
# txn = router.functions.swapExactETHForTokens(
#     amount_out_min,
#     [web3.to_checksum_address(router_address), erc20_token_address],
#     wallet_address,
#     deadline
# ).buildTransaction(transaction)

# # Sign the transaction
# signed_txn = web3.eth.account.signTransaction(txn, private_key=private_key)

# # Send the transaction
# tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

# # Wait for the transaction to be mined
# tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

# print(f'Transaction successful with hash: {tx_hash.hex()}')
