from datetime import timedelta
from odoo import models


class HoldingItemXlsx(models.AbstractModel):
    _name = 'report.hakbani_holding_item_xlsx.stock_check_template'
    _description = "Holding Item XLSX Report"
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
            'font_size': '13',
            "font_color": 'black',
            "bg_color": '#73C6B6',
            'font_name': 'Metropolis',
        })
        main_out_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '13',
            "font_color": 'black',
            "bg_color": '#EB984E',
            'font_name': 'Metropolis',
        })
        main_balance_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '13',
            "font_color": 'black',
            "bg_color": '#B2F776',
            'font_name': 'Metropolis',
        })
        main_product_format = workbook.add_format({
            'bold': 1,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': '13',
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
            'font_size': '8',
            'font_name': 'Metropolis',
        })
        format_data_right = workbook.add_format({
            "border": 1,
            "align": 'right',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '8',
            'font_name': 'Metropolis',
            "num_format": "#,##0.00",
        })
        format_data_left = workbook.add_format({
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '8',
            'font_name': 'Metropolis',
            "num_format": "#,##0.00",
        })

        worksheet = workbook.add_worksheet('Item Cart Report')

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:E', 15)

        worksheet.merge_range('A2:E3', 'Stock Check Report', main_merge_format)

        row = 5
        col = 0

        domain = [('state', '=', 'done')]
        if wizard_data.date_from and wizard_data.date_to:
            domain += [('date', '>=', wizard_data.date_from), ('date', '<=', wizard_data.date_to)]
        if wizard_data.transaction_type == 'is_in':
            domain += [('location_dest_id', '=', wizard_data.location_id.id)]
        if wizard_data.transaction_type == 'is_out':
            domain += [('location_id', '=', wizard_data.location_id.id)]
        if wizard_data.product_ids:
            domain += [('product_id', 'in', wizard_data.product_ids.ids)]

        move_records = self.env['stock.move'].search(domain)

        worksheet.write_string(row, col, 'Date From', format_data_header)
        worksheet.write_string(row, col+1, str(wizard_data.date_from), format_data_left)
        row += 1
        worksheet.write_string(row, col, 'Date To', format_data_header)
        worksheet.write_string(row, col+1, str(wizard_data.date_to), format_data_left)

        row += 2

        worksheet.write_string(row, col, 'Product', format_data_header)
        worksheet.write_string(row, col+1, 'Location', format_data_header)
        worksheet.write_string(row, col+2, 'Date', format_data_header)
        worksheet.write_string(row, col+3, 'Source', format_data_header)
        worksheet.write_string(row, col+4, 'Qty', format_data_header)

        row += 1

        prod_lis = []
        location_stock = self.env['stock.quant'].search([('location_id', '=', wizard_data.location_id.id)])

        for product in move_records:
            prod_lis.append(product.product_id.id)
        stuck_products = []
        for rec in location_stock:
            if rec.product_id.id not in prod_lis:
                stuck_products.append(rec.product_id.id)

        for proc in stuck_products:
            proc_domain = [('state', '=', 'done'),('date', '<', wizard_data.date_from),('product_id', '=', proc)]
            if wizard_data.transaction_type == 'is_in':
                proc_domain += [('location_dest_id', '=', wizard_data.location_id.id)]
            if wizard_data.transaction_type == 'is_out':
                proc_domain += [('location_id', '=', wizard_data.location_id.id)]
            stuck_prod_records = self.env['stock.move'].search(proc_domain, order='date desc', limit=1)
            for data in stuck_prod_records:
                if data.origin:
                    worksheet.write_string(row, col, data.product_id.name or '', format_data_left)
                    worksheet.write_string(row, col+1, wizard_data.location_id.complete_name or '', format_data_left)
                    worksheet.write_string(row, col+2, str(data.date) or '', format_data_left)
                    worksheet.write_string(row, col+3, data.origin or '', format_data_left)
                    worksheet.write_number(row, col+4, data.product_uom_qty, format_data_right)
                    row += 1
