from datetime import timedelta
from odoo import models


class CODPaymentXlsx(models.AbstractModel):
    _name = 'report.hakbani_item_cart_xlsx.inv_valuation_summary_template'
    _description = "Inventory Valuation XLSX Report"
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

        worksheet.set_column('A:A', 14)
        worksheet.set_column('B:D', 25)
        worksheet.set_column('E:J', 12)

        worksheet.merge_range('A2:J3', 'Item Cart Report', main_merge_format)

        row = 5
        col = 0

        domain = [('state', '=', 'done')]
        if wizard_data.date_from and wizard_data.date_to:
            domain += [('date', '>=', wizard_data.date_from), ('date', '<=', wizard_data.date_to)]
        if wizard_data.product_ids:
            domain += [('product_id', 'in', wizard_data.product_ids.ids)]

        move_records = self.env['stock.move'].search(domain)

        worksheet.write_string(row, col, 'Date From', format_data_header)
        worksheet.write_string(row, col+1, str(wizard_data.date_from), format_data_left)
        row += 1
        worksheet.write_string(row, col, 'Date To', format_data_header)
        worksheet.write_string(row, col+1, str(wizard_data.date_to), format_data_left)

        row += 2

        worksheet.merge_range(row, col+4, row, col+5, 'IN', main_in_format)
        worksheet.merge_range(row, col+6, row, col+7, 'OUT', main_out_format)
        worksheet.merge_range(row, col+8, row, col+9, 'Balance', main_balance_format)

        row += 1

        worksheet.write_string(row, col, 'Date', format_data_header)
        worksheet.write_string(row, col+1, 'Partner Name', format_data_header)
        worksheet.write_string(row, col+2, 'Description', format_data_header)
        worksheet.write_string(row, col+3, 'Source', format_data_header)
        worksheet.write_string(row, col+4, 'Qty', format_data_header)
        worksheet.write_string(row, col+5, 'Total', format_data_header)
        worksheet.write_string(row, col+6, 'Qty', format_data_header)
        worksheet.write_string(row, col+7, 'Total', format_data_header)
        worksheet.write_string(row, col+8, 'Qty', format_data_header)
        worksheet.write_string(row, col+9, 'Total', format_data_header)

        row += 1

        prod_lis = []
        for data in move_records:
            if data.location_id.id in wizard_data.location_ids.ids or data.location_dest_id.id in wizard_data.location_ids.ids:
                if data.product_id.id not in prod_lis:
                    product_data = self.env['stock.move'].search([
                        ('state', '=', 'done'),
                        ('date', '>=', wizard_data.date_from),
                        ('date', '<=', wizard_data.date_to),
                        ('product_id', '=', data.product_id.id)
                    ], order='date asc')
                    prod_lis.append(data.product_id.id)
                    worksheet.merge_range(row, col, row, col + 9, str(data.product_id.name), main_product_format)
                    row += 1
                    balance = 0.0
                    quantity = 0
                    for rec in product_data:
                        worksheet.write_string(row, col, str(rec.date) or '', format_data_left)
                        worksheet.write_string(row, col+1, rec.picking_id.partner_id.name or '', format_data_left)
                        worksheet.write_string(row, col+2, rec.reference or '', format_data_left)
                        worksheet.write_string(row, col+3, rec.origin or '', format_data_left)
                        if rec.location_id.usage in ('supplier','inventory','customer') and rec.stock_valuation_layer_ids:
                            quantity += abs(rec.stock_valuation_layer_ids[0].quantity)
                            balance += abs(rec.stock_valuation_layer_ids[0].value)
                            worksheet.write_number(row, col+4, abs(rec.stock_valuation_layer_ids[0].quantity), format_data_right)
                            worksheet.write_number(row, col+5, abs(rec.stock_valuation_layer_ids[0].value), format_data_right)
                            worksheet.write_number(row, col+6, 0, format_data_right)
                            worksheet.write_number(row, col+7, 0, format_data_right)
                        elif rec.location_id.usage == 'internal' and rec.stock_valuation_layer_ids:
                            quantity += abs(rec.stock_valuation_layer_ids[0].quantity)
                            balance += abs(rec.stock_valuation_layer_ids[0].value)
                            worksheet.write_number(row, col+4, 0, format_data_right)
                            worksheet.write_number(row, col+5, 0, format_data_right)
                            worksheet.write_number(row, col+6, abs(rec.stock_valuation_layer_ids[0].quantity), format_data_right)
                            worksheet.write_number(row, col+7, abs(rec.stock_valuation_layer_ids[0].value), format_data_right)
                        else:
                            worksheet.write_number(row, col+4, 0, format_data_right)
                            worksheet.write_number(row, col+5, 0, format_data_right)
                            worksheet.write_number(row, col+6, 0, format_data_right)
                            worksheet.write_number(row, col+7, 0, format_data_right)
                        worksheet.write_number(row, col+8, quantity, format_data_right)
                        worksheet.write_number(row, col+9, balance, format_data_right)
                        row += 1
