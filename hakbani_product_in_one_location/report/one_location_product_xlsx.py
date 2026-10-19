from datetime import timedelta
from odoo import models


class CODPaymentXlsx(models.AbstractModel):
    _name = 'report.hakbani_product_in_one_location.one_loc_product_tmpl'
    _description = "One Location Product"
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

        worksheet = workbook.add_worksheet('One Location Products')

        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 18)
        worksheet.set_column('C:E', 15)

        worksheet.merge_range('A2:E3', 'One Location Products', main_merge_format)

        row = 5
        col = 0

        domain = []
        if wizard_data.product_ids:
            domain += [('id', 'in', wizard_data.product_ids.ids)]
        else:
            domain += [('detailed_type', '=', 'product'), ('qty_available', '>', 0.0)]

        product_records = self.env['product.template'].search(domain)

        row += 1

        worksheet.write_string(row, col, 'Product', format_data_header)
        worksheet.write_string(row, col+1, 'Location', format_data_header)
        worksheet.write_string(row, col+2, 'Quantity', format_data_header)
        worksheet.write_string(row, col+3, 'Reserved', format_data_header)
        worksheet.write_string(row, col+4, 'Available', format_data_header)

        row += 1

        for product in product_records:
            if len(product.product_quant_ids) == 1:
                for line in product.product_quant_ids:
                    worksheet.write_string(row, col, product.name or '', format_data_left)
                    worksheet.write_string(row, col + 1, line.location_id.name or '', format_data_left)
                    worksheet.write_number(row, col + 2, line.quantity, format_data_right)
                    worksheet.write_number(row, col + 3, line.reserved_quantity, format_data_right)
                    worksheet.write_number(row, col + 4, line.available_quantity, format_data_right)
                    row += 1
