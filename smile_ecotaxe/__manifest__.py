# (C) 2022 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Ecotaxe",
    "version": "18.0.1.0.0",
    "author": "Smile",
    "website": "http://www.smile.fr",
    "category": "Tools",
    "license": "AGPL-3",
    "description": """
                    """,
    "depends": ["purchase"],
    "data": [
        "views/account_move_view.xml",
        "views/product_template_view.xml",
        "views/purchase_order_view.xml",
        "report/purchase_order_templates.xml",
    ],
    "uninstall_hook": "uninstall_hook",
    "installable": True,
}
