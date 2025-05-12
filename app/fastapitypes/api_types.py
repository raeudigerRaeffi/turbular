from enum import Enum


class SupportedApiTypes(str, Enum):
    aws = "aws"
    stripe = "stripe"
    mailchimp = "mailchimp"
    shopify = "shopify"
    salesforce = "salesforce"
    trello = "trello"
    linkedin = "linkedin"
    zendesk = "zendesk"
    jira = "jira"
    hubspot = "hubspot"
    clickup = "clickup"
