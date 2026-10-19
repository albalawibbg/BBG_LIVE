from datetime import timedelta
from odoo import models


class ProductMarginXlsx(models.AbstractModel):
    _name = 'report.hakbani_product_margin_report.product_margin_xlsx'
    _description = "Product Margin report wizard"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, report_detail, wizard_data):

        main_merge_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '13',
            "font_color": 'black',
            "bg_color": '#F7DC6F',
            'font_name': 'Metropolis',
        })
        main_in_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '11',
            "font_color": 'black',
            "bg_color": '#73C6B6',
            'font_name': 'Metropolis',
        })
        main_out_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '11',
            "font_color": 'black',
            "bg_color": '#EB984E',
            'font_name': 'Metropolis',
        })
        main_balance_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '11',
            "font_color": 'black',
            "bg_color": '#B2F776',
            'font_name': 'Metropolis',
        })
        main_product_format = workbook.add_format({
            'bold': 1,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': '11',
            "font_color": 'black',
            "bg_color": '#E9ECE7',
            'font_name': 'Metropolis',
        })
        format_data_header = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#F7DC6F',
            'font_size': '12',
            'font_name': 'Metropolis',
        })
        format_data_right = workbook.add_format({
            "border": 1,
            "align": 'right',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '11',
            'font_name': 'Metropolis',
            "num_format": "#,##0.00",
        })
        format_data_left = workbook.add_format({
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '11',
            'font_name': 'Metropolis',
            "num_format": "#,##0.00",
        })

        worksheet = workbook.add_worksheet('Single product Report')

        worksheet.set_column('A:J', 22)

        worksheet.merge_range('A2:I3', 'Product Margin Report', main_merge_format)

        row_num = 5
        # col = 05
        domain = [('state', 'in', ('sale','done'))]
        if wizard_data.date_from and wizard_data.date_to:
            domain += [('order_id.date_order', '>=', wizard_data.date_from)]
        if wizard_data.date_to:
            domain += [('order_id.date_order', '<=', wizard_data.date_to)]

        sale_order_lines = self.env['sale.order.line'].search(domain)

        product_data = {}

        # Iterate through sale order lines to gather data
        for line in sale_order_lines:
            product_id = line.product_id.id

            # Initialize product data if not present in the dictionary
            if product_id not in product_data:
                product_data[product_id] = {
                    'name': line.product_id.name,
                    'category': line.product_id.categ_id.name,
                    'qty_available': line.product_id.qty_available,
                    'sale_price': line.product_id.list_price,
                    'cost': line.product_id.standard_price,
                    'total_sale': 0.0,
                    'total_qty_sold': 0.0,
                    'total_margin': 0.0,
                    'margin_count': 0,
                }

            # Update total sale for the product
            product_data[product_id]['total_sale'] += line.price_subtotal
            product_data[product_id]['total_qty_sold'] += line.product_uom_qty

            # Calculate and update margin for the product

            margin = line.margin
            product_data[product_id]['total_margin'] += margin
            product_data[product_id]['margin_count'] += 1

        # Calculate average margin and margin percentage for each product
        for product_id, data in product_data.items():
            if data['margin_count'] > 0 and data['total_sale'] > 0:
                data['avg_margin'] = data['total_margin'] / data['margin_count']
                data['margin_percentage'] = (data['total_margin'] / data['total_sale']) * 100
            else:
                data['avg_margin'] = 0.0
                data['margin_percentage'] = 0.0

        # Add headers to the worksheet
        headers = ['Product Name', 'Category', 'Quantity On Hand','Sales Price', 'Cost', 'Total Sale','Total Qty Sold', 'Total Margin', 'Avg Margin', 'Margin %']
        for col_num, header in enumerate(headers):
            worksheet.write(4, col_num, header, format_data_header)

        # Write data to the worksheet
        for row_num, (product_id, data) in enumerate(product_data.items(), start=5):
            worksheet.write(row_num, 0, data['name'], main_product_format)
            worksheet.write(row_num, 1, data['category'], main_product_format)
            worksheet.write(row_num, 2, data['qty_available'], main_product_format)
            worksheet.write(row_num, 3, data['sale_price'], main_product_format)
            worksheet.write(row_num, 4, data['cost'], main_product_format)
            worksheet.write(row_num, 5, data['total_sale'], main_product_format)
            worksheet.write(row_num, 6, data['total_qty_sold'], main_product_format)
            worksheet.write(row_num, 7, str('%.2f' % data['total_margin']), main_product_format)
            worksheet.write(row_num, 8, str('%.2f' % data['avg_margin']), main_product_format)
            worksheet.write(row_num, 9, str('%.2f' % data['margin_percentage']), main_product_format)
