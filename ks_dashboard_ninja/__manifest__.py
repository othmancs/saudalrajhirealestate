{
	'name': 'Ninja Dashboard',
	'description': """
        Odoo Dashboard,
        Dashboard,
        Dashboards,
        Odoo apps,
        Dashboard app,
        HR Dashboard,
        Sales Dashboard,
        inventory Dashboard,
        Lead Dashboard,
        Opportunity Dashboard,
        CRM Dashboard,
        POS,
        POS Dashboard,
        Connectors,
        Web Dynamic,
        Report Import/Export,
        Date Filter,
        HR,
        Sales,
        Theme,
        Tile Dashboard,
        Dashboard Widgets,
        Dashboard Manager,
        Debranding,
        Customize Dashboard,
        Graph Dashboard,
        Charts Dashboard,
        Invoice Dashboard,
        Project management,
        odoo dashboard apps
        odoo dashboard app
        odoo dashboard module
        odoo modules
        dashboards
        powerful dashboards
        beautiful odoo dashboard
        odoo dynamic dashboard
        all in one dashboard
        multiple dashboard menu
        odoo dashboard portal
        beautiful odoo dashboard
        odoo best dashboard
        dashboard for management
        Odoo custom dashboard
        odoo dashboard management
        odoo dashboard apps
        create odoo dashboard
        odoo dashboard extension
        odoo dashboard module
""",

	'license': 'OPL-1',

	'currency': 'EUR',

	'price': '358.99',

	'category': 'Services',
	'version': '18.0.0.0',

	'images': ['static/description/Flag day.gif'],

	'depends': ['base', 'web', 'base_setup', 'bus','base_geolocalize','spreadsheet_dashboard', 'project'],

	'data': [
		'security/ir.model.access.csv',
		'security/ks_security_groups.xml',
		'data/ks_default_data.xml',
		'data/ks_mail_cron.xml',
		'data/sequence.xml',
		'views/ks_dashboard_ninja_view.xml',
		'views/ks_dashboard_ninja_item_view.xml',
		'views/ks_dashboard_group_by.xml',
		'views/ks_dashboard_csv_group_by.xml',
		'views/ks_dashboard_action.xml',
		'views/ks_import_dashboard_view.xml',
		'wizard/ks_create_dashboard_wiz_view.xml',
		'wizard/ks_duplicate_dashboard_wiz_view.xml',
	],

	'assets': {
		'ks_dashboard_ninja.ks_dashboard_lib': [
			'/ks_dashboard_ninja/static/lib/css/gridstack.min.css',
			'/ks_dashboard_ninja/static/lib/js/gridstack-h5.js',
			'/ks_dashboard_ninja/static/lib/js/pdfmake.min.js',
			'/ks_dashboard_ninja/static/lib/js/vfs_fonts.js',
			'ks_dashboard_ninja/static/lib/js/Animated.js',
			'ks_dashboard_ninja/static/lib/js/worldLow.js',
			'ks_dashboard_ninja/static/lib/js/map.js',
			'ks_dashboard_ninja/static/lib/js/index.js',
			'ks_dashboard_ninja/static/lib/js/pdfmake.js',
			'ks_dashboard_ninja/static/lib/js/percent.js',
			'ks_dashboard_ninja/static/lib/js/pdf.min.js',
			'ks_dashboard_ninja/static/lib/js/print.min.js',
			'ks_dashboard_ninja/static/lib/js/Dataviz.js',
			'ks_dashboard_ninja/static/lib/js/Material.js',
			'ks_dashboard_ninja/static/lib/js/Moonrise.js',
			'ks_dashboard_ninja/static/lib/js/xy.js',
			'ks_dashboard_ninja/static/lib/js/radar.js',
		],
		'web.assets_backend': [
							'web/static/lib/jquery/jquery.js',
					'ks_dashboard_ninja/static/src/css/ks_dashboard_ninja.scss',
					'ks_dashboard_ninja/static/src/css/ks_dashboard_ninja_item.css',
					'ks_dashboard_ninja/static/src/css/ks_icon_container_modal.css',
					'ks_dashboard_ninja/static/src/css/ks_dashboard_item_theme.css',
					'ks_dashboard_ninja/static/src/css/ks_input_bar.css',
					'ks_dashboard_ninja/static/src/css/ks_dn_filter.css',
					'ks_dashboard_ninja/static/src/css/ks_toggle_icon.css',
					'ks_dashboard_ninja/static/src/css/ks_flower_view.css',
					'ks_dashboard_ninja/static/src/css/ks_map_view.css',
					'ks_dashboard_ninja/static/src/css/ks_funnel_view.css',
					'ks_dashboard_ninja/static/src/css/ks_dashboard_options.css',
					'ks_dashboard_ninja/static/lib/css/Chart.min.css',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_new.js',
					'ks_dashboard_ninja/static/src/js/ks_global_functions.js',
					'ks_dashboard_ninja/static/lib/js/index.js',
					'ks_dashboard_ninja/static/lib/js/pdfmake.js',
					'ks_dashboard_ninja/static/lib/js/percent.js',
					'ks_dashboard_ninja/static/lib/js/pdf.min.js',
					'ks_dashboard_ninja/static/lib/js/print.min.js',
					'ks_dashboard_ninja/static/lib/js/Dataviz.js',
					'ks_dashboard_ninja/static/lib/js/Material.js',
					'ks_dashboard_ninja/static/lib/js/Moonrise.js',
					'ks_dashboard_ninja/static/lib/js/exporting.js',
					'ks_dashboard_ninja/static/lib/js/pdfmake.js',
					'ks_dashboard_ninja/static/lib/js/percent.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_new.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_graphs.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_kpi.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_tile.js',
					'ks_dashboard_ninja/static/src/js/editdialog.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_to_do.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_list.js',
					'ks_dashboard_ninja/static/src/js/ks_global_functions.js',
                    'ks_dashboard_ninja/static/src/js/ks_form_view_dialog.js',
					'ks_dashboard_ninja/static/lib/js/xy.js',
					'ks_dashboard_ninja/static/lib/js/radar.js',
					'ks_dashboard_ninja/static/src/css/style.css',
					'ks_dashboard_ninja/static/src/js/ks_filter_props_new.js',
					'ks_dashboard_ninja/static/src/js/domainfix.js',
					'ks_dashboard_ninja/static/src/css/ks_dashboard_ninja_pro.css',
					'ks_dashboard_ninja/static/src/css/ks_to_do_item.css',
					'ks_dashboard_ninja/static/src/xml/**/*',
					'ks_dashboard_ninja/static/src/css/ks_radial_chart.css',
					'ks_dashboard_ninja/static/src/components/**/*',
					'ks_dashboard_ninja/static/src/widgets/**/*',
					],
			   },

	'uninstall_hook': 'uninstall_hook',
}
