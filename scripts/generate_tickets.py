"""Script to construct 90 ShopEasy evaluation tickets.

Breakdown:
- 40 Easy
- 30 Medium
- 20 Hard
Splits:
- 40 Dev (18 easy, 13 medium, 9 hard)
- 50 Test (22 easy, 17 medium, 11 hard)
"""

import json
from pathlib import Path


def generate_tickets():
    tickets = []

    def add(tid, diff, split, text, oid, decision, facts, checklist):
        tickets.append(
            {
                "task_id": tid,
                "difficulty": diff,
                "split": split,
                "ticket_text": text,
                "order_id": oid,
                "gold": {
                    "decision": decision,
                    "required_facts": facts,
                    "checklist": checklist,
                },
            }
        )

    # ==========================================
    # 40 EASY TICKETS (Dev: 18, Test: 22)
    # ==========================================
    # Simple order status, tracking, and basic lookups
    easy_data = [
        # 1-18 (Dev)
        (
            "Where is my package for order ORD-1001? I haven't received any tracking updates.",
            "ORD-1001",
            "inform_status",
            ["Delivered", "Oct 14", "FedEx", "TRK94001230"],
            ["State delivery date", "Mention tracking number", "Confirm delivered"],
        ),
        (
            "Can you tell me the current tracking number and carrier for ORD-1002?",
            "ORD-1002",
            "inform_status",
            ["UPS", "TRK1Z999001", "Delivered"],
            ["State carrier", "Provide tracking number"],
        ),
        (
            "What is the status of my order ORD-1004? Is it shipped yet?",
            "ORD-1004",
            "inform_status",
            ["Processing"],
            ["State order is Processing", "Confirm not yet shipped"],
        ),
        (
            "Can I get the tracking link for order ORD-1005?",
            "ORD-1005",
            "inform_status",
            ["In Transit", "USPS", "TRK94055102"],
            ["State order is In Transit", "Provide USPS tracking number"],
        ),
        (
            "What items did I buy in order ORD-1008?",
            "ORD-1008",
            "inform_status",
            ["Classic Oxford Shirt", "Silk Tie", "110.00"],
            ["List items in order", "State total amount"],
        ),
        (
            "Has order ORD-1014 left the warehouse?",
            "ORD-1014",
            "inform_status",
            ["Shipped", "USPS", "TRK94055114"],
            ["Confirm order has shipped", "Provide tracking number"],
        ),
        (
            "When was order ORD-1009 delivered?",
            "ORD-1009",
            "inform_status",
            ["Delivered", "Sep 29", "UPS"],
            ["State delivery date of Sep 29"],
        ),
        (
            "What is the total amount charged for order ORD-1015?",
            "ORD-1015",
            "inform_status",
            ["129.99", "Delivered"],
            ["State total charge of $129.99", "Confirm delivery"],
        ),
        (
            "Did order ORD-1017 use any discount code?",
            "ORD-1017",
            "inform_status",
            ["FALL10", "11.50", "103.50"],
            ["Mention coupon FALL10", "State discount amount"],
        ),
        (
            "Can you verify the delivery address or carrier for ORD-1019?",
            "ORD-1019",
            "inform_status",
            ["UPS", "TRK1Z999019", "Oct 12"],
            ["Identify carrier as UPS", "Confirm delivery date"],
        ),
        (
            "What is the status of my pending order ORD-1022?",
            "ORD-1022",
            "inform_status",
            ["Pending", "60.99"],
            ["Confirm status is Pending", "State order amount"],
        ),
        (
            "Where is order ORD-1025 right now? I need it today.",
            "ORD-1025",
            "inform_status",
            ["Out for delivery", "UPS", "TRK1Z999025"],
            ["State out for delivery", "Mention carrier UPS"],
        ),
        (
            "What is the total and items in order ORD-1023?",
            "ORD-1023",
            "inform_status",
            ["Celestial Night Lamp", "Starry Sky Tapestry", "72.99"],
            ["List items", "State total amount of $72.99"],
        ),
        (
            "What carrier was used for order ORD-1027?",
            "ORD-1027",
            "inform_status",
            ["FedEx", "TRK94001027", "Oct 09"],
            ["State carrier FedEx", "Provide tracking number"],
        ),
        (
            "Check status for unknown order ORD-9999 please.",
            "ORD-9999",
            "order_not_found",
            ["not found", "ORD-9999"],
            ["State order was not found", "Ask customer to verify order number"],
        ),
        (
            "What is your standard return window duration?",
            "NONE",
            "inform_policy",
            ["30 days", "full refund"],
            ["State 30-day window for full refunds"],
        ),
        (
            "How long do I have to report damaged items according to store policy?",
            "NONE",
            "inform_policy",
            ["7 days"],
            ["State 7-day reporting requirement for damaged goods"],
        ),
        (
            "Do you offer store credit if I return after 30 days?",
            "NONE",
            "inform_policy",
            ["31 to 60 days", "store credit"],
            ["State 31-60 day window for store credit"],
        ),
        # 19-40 (Test)
        (
            "I need an update on order ORD-1002.",
            "ORD-1002",
            "inform_status",
            ["Delivered", "Aug 20", "UPS"],
            ["Confirm delivery", "State delivered date"],
        ),
        (
            "What is the carrier tracking number for order ORD-1007?",
            "ORD-1007",
            "inform_status",
            ["FedEx", "TRK94008821", "Oct 15"],
            ["Provide FedEx tracking number", "Confirm delivery on Oct 15"],
        ),
        (
            "Is order ORD-1016 shipped yet?",
            "ORD-1016",
            "inform_status",
            ["Processing", "44.49"],
            ["Confirm order is still Processing", "Confirm not yet shipped"],
        ),
        (
            "What items are in order ORD-1018?",
            "ORD-1018",
            "inform_status",
            ["Cast Iron Skillet", "Processing"],
            ["State item name", "State quantity 2", "Confirm Processing status"],
        ),
        (
            "Can you tell me the tracking status for order ORD-1021?",
            "ORD-1021",
            "inform_status",
            ["Delivered", "Oct 13", "FedEx"],
            ["Confirm delivered on Oct 13", "Provide FedEx tracking"],
        ),
        (
            "What did I pay for shipping on order ORD-1001?",
            "ORD-1001",
            "inform_status",
            ["5.99"],
            ["State shipping fee of $5.99"],
        ),
        (
            "What coupon was applied on order ORD-1004?",
            "ORD-1004",
            "inform_status",
            ["SAVE20", "20.00"],
            ["Confirm coupon SAVE20 was applied", "State discount of $20.00"],
        ),
        (
            "Is order ORD-1029 still pending?",
            "ORD-1029",
            "inform_status",
            ["Pending", "70.99"],
            ["Confirm order status is Pending"],
        ),
        (
            "Check tracking number for order ORD-1030.",
            "ORD-1030",
            "inform_status",
            ["USPS", "TRK94055130", "Oct 14"],
            ["Provide USPS tracking", "Confirm delivery on Oct 14"],
        ),
        (
            "What carrier delivered order ORD-1024?",
            "ORD-1024",
            "inform_status",
            ["FedEx", "TRK94001024", "Aug 23"],
            ["State carrier FedEx", "Confirm delivered on Aug 23"],
        ),
        (
            "What was the total order price for ORD-1028?",
            "ORD-1028",
            "inform_status",
            ["140.00", "Delivered"],
            ["State total price of $140.00"],
        ),
        (
            "Did order ORD-1012 have any discounts?",
            "ORD-1012",
            "inform_status",
            ["TACTICAL10", "13.50", "121.50"],
            ["Mention coupon TACTICAL10", "State final total $121.50"],
        ),
        (
            "Where is order ORD-1005 currently located in transit?",
            "ORD-1005",
            "inform_status",
            ["In Transit", "Oct 18", "USPS"],
            ["State in transit", "Mention estimated arrival Oct 18"],
        ),
        (
            "Verify order ORD-1020 order and delivery dates.",
            "ORD-1020",
            "inform_status",
            ["Jul 20", "Jul 25", "Delivered"],
            ["State order date Jul 20", "State delivery date Jul 25"],
        ),
        (
            "Please check if order ORD-0000 exists in your database.",
            "ORD-0000",
            "order_not_found",
            ["not found", "ORD-0000"],
            ["State order not found", "Advise checking order ID"],
        ),
        (
            "What is your standard shipping delivery time frame?",
            "NONE",
            "inform_policy",
            ["3–5 business days"],
            ["State 3-5 business days for standard shipping"],
        ),
        (
            "How much is the return shipping fee if I return an item?",
            "NONE",
            "inform_policy",
            ["5.99"],
            ["State standard $5.99 return shipping fee"],
        ),
        (
            "Can I stack two coupon codes on a single purchase?",
            "NONE",
            "inform_policy",
            ["one", "cannot be stacked"],
            ["Clarify only one coupon code per order"],
        ),
        (
            "What happens if a package has no tracking update for over a week?",
            "NONE",
            "inform_policy",
            ["7 days", "lost", "reshipment", "refund"],
            ["Explain lost package policy after 7 days"],
        ),
        (
            "Do I get a cash refund if I return after 45 days?",
            "NONE",
            "inform_policy",
            ["store credit", "no cash"],
            ["Explain returns between 31-60 days receive store credit only"],
        ),
        (
            "What is the status of order ORD-1013?",
            "ORD-1013",
            "inform_status",
            ["Delivered", "Jun 20", "400.00"],
            ["Confirm delivered on Jun 20", "State total amount"],
        ),
        (
            "Can you tell me the tracking carrier for ORD-1003?",
            "ORD-1003",
            "inform_status",
            ["UPS", "TRK1Z999002", "Jul 06"],
            ["Provide UPS tracking", "Confirm delivery on Jul 06"],
        ),
    ]

    for idx, (text, oid, dec, facts, cl) in enumerate(easy_data, 1):
        diff = "easy"
        split = "dev" if idx <= 18 else "test"
        add(f"ticket_{idx:03d}", diff, split, text, oid, dec, facts, cl)

    # ==========================================
    # 30 MEDIUM TICKETS (Dev: 13, Test: 17)
    # ==========================================
    # Returns within 30 days vs 31-60 days vs >60 days; order cancellations in Processing vs Shipped
    medium_data = [
        # 41-53 (Dev)
        (
            "I would like to return the sweater from order ORD-1001 for a full refund. Delivered 3 days ago.",
            "ORD-1001",
            "approve_return_refund",
            ["approved", "30 days", "5.99", "95.98"],
            [
                "Approve refund request within 30-day window",
                "Mention $5.99 return shipping deduction",
            ],
        ),
        (
            "I want to return the boots from ORD-1002. They were delivered on Aug 20 and it's now Oct 17. Can I get my money back?",
            "ORD-1002",
            "offer_store_credit_only",
            ["store credit", "30 days", "58 days", "no cash refund"],
            [
                "Explain 30-day refund window has passed",
                "Offer store credit under 31-60 day window",
                "Deny cash refund",
            ],
        ),
        (
            "I want to return order ORD-1003. Delivered back in July. Please refund my card.",
            "ORD-1003",
            "deny_return_past_window",
            ["ineligible", "60 days", "Jul 06"],
            [
                "Deny return request",
                "Explain delivery was over 60 days ago",
                "Explain ineligible for both refund and store credit",
            ],
        ),
        (
            "Please cancel my order ORD-1004 immediately. I changed my mind.",
            "ORD-1004",
            "cancel_order_approved",
            ["cancelled", "Processing", "179.99"],
            [
                "Approve cancellation as order is in Processing",
                "Confirm authorization will be released",
            ],
        ),
        (
            "Cancel my order ORD-1005 right now please.",
            "ORD-1005",
            "deny_cancellation_in_transit",
            ["cannot be cancelled", "In Transit", "return upon arrival"],
            [
                "Deny direct cancellation because order is In Transit",
                "Instruct customer to initiate return after delivery",
            ],
        ),
        (
            "I want to return the aviator sunglasses from ORD-1009 delivered Sep 29. Can I get a full refund?",
            "ORD-1009",
            "approve_return_refund",
            ["approved", "18 days", "30 days", "full refund"],
            [
                "Approve full refund (within 30 days)",
                "Mention standard return steps and $5.99 return fee",
            ],
        ),
        (
            "I want to return rain boots from ORD-1010. Delivered Sep 05. I want a refund to my credit card.",
            "ORD-1010",
            "offer_store_credit_only",
            ["store credit", "42 days", "30-day window expired"],
            [
                "Deny credit card refund",
                "Offer store credit as order is within 31-60 day window",
            ],
        ),
        (
            "Cancel order ORD-1014 please. I do not want it anymore.",
            "ORD-1014",
            "deny_cancellation_in_transit",
            ["cannot cancel", "Shipped", "USPS", "TRK94055114"],
            [
                "State order has already shipped",
                "Explain cannot be intercepted",
                "Advise returning item after delivery",
            ],
        ),
        (
            "I want to return the keyboard from ORD-1015 delivered Sep 24.",
            "ORD-1015",
            "approve_return_refund",
            ["approved", "23 days", "30 days", "129.99"],
            [
                "Approve return for refund (within 30 days)",
                "Explain $5.99 return shipping fee deducted",
            ],
        ),
        (
            "I bought a dress on ORD-1019 delivered on Oct 12. Size does not fit, can I return for refund?",
            "ORD-1019",
            "approve_return_refund",
            ["approved", "5 days", "30 days", "180.00"],
            ["Approve return within 30-day window", "State refund to original card"],
        ),
        (
            "I want to return guitar strings from ORD-1020 delivered July 25.",
            "ORD-1020",
            "deny_return_past_window",
            ["ineligible", "over 60 days", "Jul 25"],
            ["Deny return request", "Explain past 60-day limit"],
        ),
        (
            "Cancel my pending order ORD-1022.",
            "ORD-1022",
            "cancel_order_approved",
            ["cancelled", "Pending", "60.99"],
            [
                "Confirm cancellation of Pending order",
                "Confirm release of $60.99 authorization",
            ],
        ),
        (
            "I want to return lamp and tapestry from ORD-1023 delivered Oct 07.",
            "ORD-1023",
            "approve_return_refund",
            ["approved", "10 days", "30 days", "72.99"],
            ["Approve return request", "Explain standard return shipping fee"],
        ),
        # 54-70 (Test)
        (
            "Can I return order ORD-1024? Delivered Aug 23, want refund to debit card.",
            "ORD-1024",
            "offer_store_credit_only",
            ["store credit", "55 days", "30 days passed"],
            [
                "Deny cash/card refund",
                "Offer store credit under 60-day policy",
            ],
        ),
        (
            "Cancel order ORD-1025. It is out for delivery today.",
            "ORD-1025",
            "deny_cancellation_in_transit",
            ["cannot cancel", "Out for delivery", "return upon receipt"],
            [
                "Deny cancellation request",
                "Explain package is with driver/carrier",
            ],
        ),
        (
            "Return cowboy hat from ORD-1027 delivered Oct 09 for refund.",
            "ORD-1027",
            "approve_return_refund",
            ["approved", "8 days", "30 days", "157.50"],
            ["Approve refund request within 30-day window"],
        ),
        (
            "Return canvas jacket from ORD-1028 delivered July 15. Want store credit or refund.",
            "ORD-1028",
            "deny_return_past_window",
            ["ineligible", "over 60 days", "July 15"],
            ["Deny both refund and store credit", "Cite >60 days policy"],
        ),
        (
            "Cancel order ORD-1029 immediately, ordered yesterday.",
            "ORD-1029",
            "cancel_order_approved",
            ["cancelled", "Pending", "70.99"],
            ["Approve cancellation of pending order"],
        ),
        (
            "Return sweater ORD-1001 delivered Oct 14.",
            "ORD-1001",
            "approve_return_refund",
            ["approved", "30 days", "95.98"],
            ["Approve return", "State refund to original payment"],
        ),
        (
            "Return espresso machine ORD-1013 delivered Jun 20. Need refund.",
            "ORD-1013",
            "deny_return_past_window",
            ["ineligible", "over 60 days", "Jun 20"],
            ["Deny return", "Explain purchase is over 100 days old"],
        ),
        (
            "I want to cancel ORD-1016, still in processing.",
            "ORD-1016",
            "cancel_order_approved",
            ["cancelled", "Processing", "44.49"],
            ["Approve cancellation", "Confirm authorization hold released"],
        ),
        (
            "Return purse from ORD-1017 delivered Aug 30. Want my money back.",
            "ORD-1017",
            "offer_store_credit_only",
            ["store credit", "48 days", "no card refund"],
            ["Deny original card refund", "Offer store credit (31-60 days)"],
        ),
        (
            "Can I return ORD-1023 items delivered Oct 07 for a full refund?",
            "ORD-1023",
            "approve_return_refund",
            ["approved", "30 days", "full refund"],
            ["Confirm eligibility for full refund"],
        ),
        (
            "Cancel order ORD-1018 currently processing in warehouse.",
            "ORD-1018",
            "cancel_order_approved",
            ["cancelled", "Processing"],
            ["Approve cancellation of processing order"],
        ),
        (
            "I want to return hiking boots ORD-1002 delivered Aug 20. I insist on a card refund.",
            "ORD-1002",
            "offer_store_credit_only",
            ["store credit", "policy", "cannot refund card"],
            ["Reiterate card refund is impossible after 30 days", "Offer store credit"],
        ),
        (
            "Return scarf from ORD-1030 delivered Oct 14.",
            "ORD-1030",
            "approve_return_refund",
            ["approved", "30 days", "Oct 14"],
            ["Approve return for refund"],
        ),
        (
            "Cancel order ORD-1011 which has been delayed in transit for two weeks.",
            "ORD-1011",
            "declare_lost_or_cancel",
            ["delayed", "lost package policy", "7 days", "refund or reshipment"],
            [
                "Acknowledge tracking has no scan for >7 days",
                "Apply lost package policy",
                "Offer full refund or free replacement",
            ],
        ),
        (
            "Return sunglasses ORD-1009 delivered Sep 29.",
            "ORD-1009",
            "approve_return_refund",
            ["approved", "18 days", "Sep 29"],
            ["Approve return within 30-day window"],
        ),
        (
            "I want to return duffel bag ORD-1003 delivered July 06.",
            "ORD-1003",
            "deny_return_past_window",
            ["ineligible", "expired", "60 days"],
            ["Explain order is over 3 months old", "Deny return"],
        ),
        (
            "Cancel order ORD-1008 placed today.",
            "ORD-1008",
            "cancel_order_approved",
            ["cancelled", "Pending", "110.00"],
            ["Cancel pending order ORD-1008"],
        ),
    ]

    for idx, (text, oid, dec, facts, cl) in enumerate(medium_data, 41):
        diff = "medium"
        split = "dev" if idx <= 53 else "test"
        add(f"ticket_{idx:03d}", diff, split, text, oid, dec, facts, cl)

    # ==========================================
    # 20 HARD TICKETS (Dev: 9, Test: 11)
    # ==========================================
    # Multi-issue tickets: double charges + damaged items, forgot coupon + address change, delayed package lost in transit
    hard_data = [
        # 71-79 (Dev)
        (
            "You charged me twice for order ORD-1006 ($50.99 each)! Also, when will this coffee set ship?",
            "ORD-1006",
            "refund_duplicate_and_inform_status",
            [
                "duplicate charge",
                "50.99",
                "refunded",
                "Processing",
                "3-5 business days",
            ],
            [
                "Acknowledge and refund duplicate charge ch_1006_b",
                "Confirm original charge is valid",
                "Answer shipping question: order is Processing and will ship soon",
            ],
        ),
        (
            "My glass decanter set for order ORD-1007 arrived completely shattered with broken glass everywhere! I demand an immediate refund or replacement and I am NOT paying return shipping for broken glass.",
            "ORD-1007",
            "approve_damaged_remedy",
            [
                "damaged item policy",
                "replacement or full refund",
                "no return shipping fee",
                "photo proof",
            ],
            [
                "Apologize for damaged delivery",
                "Waive return shipping fee under Damaged Item Policy",
                "Offer choice of free immediate replacement or 100% full refund",
                "Request photo proof if required by policy",
            ],
        ),
        (
            "I placed order ORD-1008 yesterday and forgot to use my 15% discount coupon SAVE15. Can you apply it retroactively or refund the difference?",
            "ORD-1008",
            "apply_courtesy_credit_for_coupon",
            ["SAVE15", "within 24 hours", "courtesy store credit", "15%"],
            [
                "Check that order was placed within 24 hours",
                "Apply coupon policy rule: cannot modify completed charge directly",
                "Issue courtesy store credit for the 15% discount difference ($16.50)",
            ],
        ),
        (
            "My chair on order ORD-1011 has had zero tracking updates since Oct 04 on FedEx. It is now Oct 17. Where is it? I need it for work on Monday!",
            "ORD-1011",
            "declare_lost_package",
            [
                "no scan for over 7 days",
                "declared lost",
                "free reshipment",
                "full refund",
            ],
            [
                "Verify last scan was over 7 consecutive days ago (Oct 04)",
                "Declare package officially lost in transit per policy",
                "Offer customer choice between expedited free reshipment and full $320 refund",
            ],
        ),
        (
            "You sent me the wrong color on order ORD-1012! I ordered Black and got Green. Do not make me pay to ship this back.",
            "ORD-1012",
            "store_error_free_exchange",
            [
                "wrong item",
                "store error",
                "free return shipping",
                "correct item Black",
                "121.50",
            ],
            [
                "Acknowledge store error (wrong color delivered)",
                "Confirm free return shipping label provided at zero cost",
                "Arrange exchange for correct Black color or full refund",
            ],
        ),
        (
            "I noticed two charges of $99.98 on my card for order ORD-1018 on Oct 15! Also, can I still cancel this order before it leaves your warehouse?",
            "ORD-1018",
            "refund_duplicate_and_cancel_order",
            ["duplicate charge refunded", "99.98", "order cancelled", "Processing"],
            [
                "Identify two identical charges of $99.98 (ch_1018_a and ch_1018_b)",
                "Refund duplicate charge of $99.98",
                "Cancel the processing order so customer is not billed for either charge",
            ],
        ),
        (
            "My yellow martial arts tracksuit on order ORD-1021 arrived with a broken zipper right out of the bag. Delivered Oct 13. What are my options?",
            "ORD-1021",
            "approve_damaged_remedy",
            [
                "damaged/defective",
                "within 7 days",
                "free replacement or refund",
                "no return fee",
            ],
            [
                "Verify reported within 7 days of delivery (Oct 13)",
                "Offer free replacement or full refund under Defective Items policy",
                "Waive return fee",
            ],
        ),
        (
            "My bank alerted me to two charges of $189.00 for order ORD-1026. Please fix this immediately, I am furious!",
            "ORD-1026",
            "refund_duplicate_charge",
            ["duplicate charge", "189.00", "refunded immediately", "3–5 business days"],
            [
                "Confirm duplicate charge ch_1026_b on Oct 14",
                "Issue immediate refund of $189.00",
                "Explain funds appear in 3-5 business days",
                "Confirm primary order ORD-1026 remains in Processing",
            ],
        ),
        (
            "My wool scarf from order ORD-1030 arrived with dark oily stains on the fabric. Delivered Oct 14. I want a clean replacement.",
            "ORD-1030",
            "approve_damaged_remedy",
            ["damaged on arrival", "within 7 days", "free replacement shipment"],
            [
                "Acknowledge stained arrival within 7-day report window",
                "Issue free replacement shipment with waived return fees",
            ],
        ),
        # 80-90 (Test)
        (
            "Order ORD-1006 has two charges on my statement ($50.99 each). Please refund one and tell me when it arrives.",
            "ORD-1006",
            "refund_duplicate_and_inform_status",
            ["duplicate refunded", "50.99", "Processing", "standard shipping"],
            ["Refund duplicate charge", "State order is currently Processing"],
        ),
        (
            "I received broken glass for order ORD-1007. I want a replacement immediately and don't charge me return shipping.",
            "ORD-1007",
            "approve_damaged_remedy",
            ["damaged item", "free replacement", "no return shipping fee"],
            ["Offer free replacement", "Confirm zero return shipping charge"],
        ),
        (
            "I placed ORD-1029 yesterday and forgot coupon code VIP10. Can I get a discount?",
            "ORD-1029",
            "apply_courtesy_credit_for_coupon",
            ["within 24 hours", "courtesy store credit", "VIP10"],
            ["Apply 24-hour courtesy rule", "Issue store credit for coupon amount"],
        ),
        (
            "FedEx has not updated tracking on ORD-1011 in almost two weeks. I want a full refund right now.",
            "ORD-1011",
            "declare_lost_package",
            ["no scan for over 7 days", "declared lost", "full refund of 320.00"],
            ["Declare lost in transit", "Process full refund of $320.00"],
        ),
        (
            "You shipped green instead of black for ORD-1012. Send me the black one right away with a free return label.",
            "ORD-1012",
            "store_error_free_exchange",
            ["wrong color", "free return label", "black replacement"],
            [
                "Acknowledge wrong item",
                "Provide free return shipping",
                "Send correct item",
            ],
        ),
        (
            "ORD-1018 was charged twice on my card ($99.98). Please cancel the whole thing and refund both charges.",
            "ORD-1018",
            "refund_duplicate_and_cancel_order",
            ["two charges of 99.98", "cancelled", "full refund"],
            [
                "Refund duplicate charge",
                "Cancel order in Processing",
                "Release initial charge",
            ],
        ),
        (
            "Tracksuit zipper on ORD-1021 broke on day one. Delivered Oct 13. Send replacement.",
            "ORD-1021",
            "approve_damaged_remedy",
            ["defective item", "within 7 days", "free replacement"],
            ["Approve free replacement under defective item policy"],
        ),
        (
            "ORD-1026 has double billing on my statement ($189.00 each). Refund the extra one.",
            "ORD-1026",
            "refund_duplicate_charge",
            ["duplicate charge", "189.00 refunded", "3-5 business days"],
            ["Refund duplicate charge", "State 3-5 days refund timeline"],
        ),
        (
            "My ORD-1030 scarf has black stains. Can I get a full refund without returning?",
            "ORD-1030",
            "approve_damaged_remedy",
            ["stained/damaged", "within 7 days", "refund approved", "photo required"],
            ["Approve refund under damaged policy", "Request photo proof"],
        ),
        (
            "I have two issues: ORD-1006 was charged twice, and I want to change the delivery address.",
            "ORD-1006",
            "refund_duplicate_and_update_address",
            ["duplicate charge refunded", "50.99", "Processing", "address updated"],
            ["Refund duplicate charge", "Update shipping address while in Processing"],
        ),
        (
            "ORD-1007 glass was broken and ORD-1008 had no coupon applied. Help with both.",
            "ORD-1007",
            "multi_order_resolution",
            ["ORD-1007 damaged free replacement", "ORD-1008 courtesy coupon credit"],
            [
                "Address damaged decanter in ORD-1007",
                "Address coupon courtesy credit in ORD-1008",
            ],
        ),
    ]

    for idx, (text, oid, dec, facts, cl) in enumerate(hard_data, 71):
        diff = "hard"
        split = "dev" if idx <= 79 else "test"
        add(f"ticket_{idx:03d}", diff, split, text, oid, dec, facts, cl)

    out_path = Path(__file__).resolve().parent.parent / "eval" / "tasks.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(t) + "\n" for t in tickets)

    print(f"Generated {len(tickets)} tickets to {out_path}")
    dev_count = sum(1 for t in tickets if t["split"] == "dev")
    test_count = sum(1 for t in tickets if t["split"] == "test")
    easy_count = sum(1 for t in tickets if t["difficulty"] == "easy")
    med_count = sum(1 for t in tickets if t["difficulty"] == "medium")
    hard_count = sum(1 for t in tickets if t["difficulty"] == "hard")
    print(f"Splits: {dev_count} dev, {test_count} test")
    print(f"Difficulties: {easy_count} easy, {med_count} medium, {hard_count} hard")


if __name__ == "__main__":
    generate_tickets()
