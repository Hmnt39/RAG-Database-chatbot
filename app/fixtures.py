from pymongo import InsertOne
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)


def generate_accounts():
    industries = ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"]
    regions = ["North", "South", "East", "West"]
    now = datetime.utcnow()

    accounts = []
    for i in range(1, 21):
        accounts.append({
            "accountCode": f"ACC{str(i).zfill(3)}",
            "accountName": f"Account {i}",
            "industry": industries[(i - 1) % len(industries)],
            "region": regions[(i - 1) % len(regions)],
            "annualRevenue": random.randint(1_000_000, 10_000_000),
            "createdAt": now,
            "updatedAt": now,
        })
    return accounts


def generate_opportunity(i: int, account: dict):
    stages = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
    sources = ["Website", "Referral", "Partner", "Cold Call", "Campaign", "Email"]
    owners = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Helen"]
    currencies = ["USD", "EUR", "INR"]

    stage = stages[i % len(stages)]
    amount = random.randint(5_000, 500_000)

    probability_map = {
        "Prospecting": 10,
        "Qualification": 25,
        "Proposal": 50,
        "Negotiation": 75,
        "Closed Won": 100,
        "Closed Lost": 0,
    }

    created_date = datetime(
        year=2024,
        month=random.randint(1, 12),
        day=random.randint(1, 28),
    )
    close_date = created_date + timedelta(days=random.randint(10, 180))

    status = "Open"
    is_active = True

    if stage == "Closed Won":
        status = "Won"
        is_active = False
    elif stage == "Closed Lost":
        status = "Lost"
        is_active = False

    return {
        "opportunityCode": f"OPP{str(i).zfill(6)}",
        "opportunityName": f"Opportunity {i}",
        "accountId": account["_id"],
        "accountCode": account["accountCode"],
        "accountName": account["accountName"],
        "stage": stage,
        "source": sources[i % len(sources)],
        "owner": owners[i % len(owners)],
        "amount": amount,
        "currency": currencies[i % len(currencies)],
        "probability": probability_map[stage],
        "expectedCloseDate": close_date,
        "status": status,
        "isActive": is_active,
        "description": f"CRM opportunity {i} for {account['accountName']}",
        "createdAt": created_date,
        "updatedAt": datetime.utcnow(),
    }


def load_crm_fixture(db_client):
    """Load CRM fixture data into MongoDB using the provided db_client."""
    if db_client.db is None:
        raise RuntimeError("Database client not connected. Call db_client.connect() first.")
    
    accounts_collection = db_client.db["accounts"]
    opportunities_collection = db_client.db["opportunities"]

    if opportunities_collection.count_documents({}) > 0:
        logger.info("Opportunities collection already has data. Skipping fixture load.")
        return
    
    accounts_collection.delete_many({})
    opportunities_collection.delete_many({})

    accounts = generate_accounts()
    account_result = accounts_collection.insert_many(accounts)

    inserted_accounts = list(
        accounts_collection.find(
            {"_id": {"$in": account_result.inserted_ids}},
            {"accountCode": 1, "accountName": 1}
        )
    )

    total_docs = 100000
    batch_size = 5000
    operations = []

    for i in range(1, total_docs + 1):
        account = inserted_accounts[(i - 1) % 20]
        opportunity = generate_opportunity(i, account)
        operations.append(InsertOne(opportunity))

        if len(operations) == batch_size:
            opportunities_collection.bulk_write(operations)
            logger.info(f"Inserted {i} opportunities")
            operations = []

    if operations:
        opportunities_collection.bulk_write(operations)

    opportunities_collection.create_index("accountId")
    opportunities_collection.create_index("stage")
    opportunities_collection.create_index("owner")
    opportunities_collection.create_index("opportunityCode", unique=True)

    logger.info("Fixture loaded successfully")
    logger.info(f"Accounts: {accounts_collection.count_documents({})}")
    logger.info(f"Opportunities: {opportunities_collection.count_documents({})}")