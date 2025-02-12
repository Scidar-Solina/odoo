{
    'name': 'Guest Management System',
    'version': '1.0',
    'summary': 'Manage guest check-ins and bookings inside Odoo',
    'category': 'Hospitality',
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/gms_guest_view.xml',
    ],
    'installable': True,
    'application': True,
}
