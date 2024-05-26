from web3 import Web3
from dotenv import load_dotenv
import os
import json
import datetime

# Load environment variables from .env file
load_dotenv()

# Get environment variables
wallet_address = os.getenv('WALLET_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')
router_abi_json = os.getenv('ROUTER_ABI_JSON')
erc20_token_abi_json = os.getenv('ERC20_TOKEN_ABI_JSON')

# Connect to the BSC testnet
web3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-1-s1.binance.org:8545/'))

# Check if connected
if not web3.is_connected():
    print("Failed to connect to the BSC testnet.")
    exit()

print("Connected to the BSC testnet.")

# V2 router contract address and ABI
router_address = '0x9bC24Ea4EfCaFF2f1DDad85aEE5fA2100E21beEe'
router_abi = json.loads(router_abi_json)

# Create contract instance
router = web3.eth.contract(address=router_address, abi=router_abi)
print("Router instance created.")

# Token details
erc20_token_address = '0xab1a4d4f1d656d2450692d237fdd6c7f9146e814'
erc20_token_abi = json.loads(erc20_token_abi_json)

# Create contract instance for the ERC20 token
# erc20_token = web3.eth.contract(address=erc20_token_address, abi=erc20_token_abi)
print("ERC20 token instance created.")

# Amount of BNB to swap (in Wei)
amount_in_wei = web3.to_wei(0.01, 'ether')
print("Amount in Wei:", amount_in_wei)
print("Wallet address:", wallet_address)

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

try:
    # Retrieve the current time
    now = datetime.datetime.now()
    current_time_str = now.strftime("%H:%M:%S.%f")
    # print(f"Current time: {current_time_str}")

    # Calculate the deadline (10 minutes from now)
    deadline_timestamp = now + datetime.timedelta(minutes=10)
    deadline = int(deadline_timestamp.timestamp())
    print(f"Deadline (10 minutes from now): {deadline} (timestamp)")

except Exception as e:
    print(f"Error getting latest time: {e}")

# Call to the read function
try:
    weth_address = router.functions.WETH().call()
    print("WETH address:", weth_address)
except Exception as e:
    print("Error calling WETH function:", e)

# Fetch the current exchange rate and calculate the minimum amount of tokens to accept (for slippage tolerance)
try:
    path = [web3.to_checksum_address(weth_address), web3.to_checksum_address(erc20_token_address) ]
    amounts_out = router.functions.getAmountsOut(amount_in_wei, path).call()
    amount_out_min = amounts_out[1]
    print("Amount out min:", amount_out_min)
except Exception as e:
    print("Error calling getAmountsOut function:", e)

# Adjust for slippage tolerance
amount_out_min = int(amount_out_min * (1 - slippage_tolerance / 100))
amount_out=web3.to_wei(amount_out_min, 'ether')
print("Amount out:", amount_out)

# Build the transaction
try:
    txn = router.functions.swapExactETHForTokens(
        amount_in_wei,
        amount_out,
        path,
        wallet_address,
        deadline
    )

    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)

    # Send the transaction
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print(f'Transaction successful with hash: {tx_hash.hex()}')
except Exception as e:
    print("Error during the transaction process:", e)
