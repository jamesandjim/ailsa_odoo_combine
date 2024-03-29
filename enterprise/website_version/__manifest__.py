{
    'name': 'Website Versioning',
    'category': 'Website',
    'summary': 'Allow to save all the versions of your website and allow to perform AB testing.',
    'version': '1.0',
    'description': """
OpenERP Website CMS
===================

        """,
    'depends': ['website', 'mail', 'google_account'],
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'views/website_version_templates.xml',
        'views/marketing_view.xml',
        'views/website_version_views.xml',
        'data/data.xml',
    ],
    'demo': [
        'data/demo.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'application': False,
    'license': 'OEEL-1',
}
