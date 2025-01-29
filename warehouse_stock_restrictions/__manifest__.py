{
    'name': "Warehouse Restrictions",
    'summary': """
         Warehouse and Stock Location Restriction on Users.""",

    'description': """
        This Module Restricts the User from Accessing Warehouse and 
        Process Stock Moves other than allowed to Warehouses and Stock Locations.
    """,
    'version': '0.2',

    'author': "",
    'website': "",
    'license': 'LGPL-3',
    'category': 'Warehouse',
    'depends': [
        'base',
        'stock'
    ],

    'data': [
        'security/security.xml',
        'views/users_view.xml',
    ],

}
