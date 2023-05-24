{
    "name": "Purchase Requisition Custom",
    "version": "15.0.1.1.1",
    "category": "Purchase Requisition",
    "depends": ["purchase_requisition", "stock_request"],
    "data": [
        "security/purchase_requisition_security.xml",
        "security/ir.model.access.csv",
        "wizard/tender_recommendation_wizard.xml",
        "views/purchase_requisition.xml",
        "views/res_config_settings_views.xml",

    ],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
