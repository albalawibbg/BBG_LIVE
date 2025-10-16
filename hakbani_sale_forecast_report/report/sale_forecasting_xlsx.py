from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models
import calendar


class SaleForecast(models.AbstractModel):
    _name = 'report.hakbani_sale_forecast_report.sale_forecast_template'
    _description = "Sale Forecast XLSX Report"
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
        format_data_right_red = workbook.add_format({
            "border": 1,
            "align": 'right',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#F72E0A',
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

        today_date = datetime.today()
        end = (today_date - relativedelta(months=1))
        res = calendar.monthrange(end.year, end.month)
        day = res[1]
        end_date = datetime(end.year, end.month, day, 23, 59, 59)
        past_date = end_date - relativedelta(months=(int(wizard_data.avg_period) - 1))
        start_date = datetime(past_date.year, past_date.month, 1)

        sale_records = self.env['sale.order.line'].search([
            ('state', '=', 'sale'),
            ('order_id.date_order', '>=', start_date),
            ('order_id.date_order', '<=', end_date),
        ])

        worksheet = workbook.add_worksheet('Sale Forecast Report')

        worksheet.set_column('A:B', 25)
        worksheet.set_column('C:L', 12)

        worksheet.merge_range('A2:L3', 'Plan Sale Forecast Report', main_merge_format)

        row = 5
        col = 0

        worksheet.write_string(row, col, 'Item', format_data_header)
        worksheet.write_string(row, col+1, 'Category', format_data_header)
        worksheet.write_string(row, col+2, 'Qty Available', format_data_header)
        worksheet.write_string(row, col+3, 'Qty To Way', format_data_header)
        worksheet.write_string(row, col+4, 'Total', format_data_header)
        worksheet.write_string(row, col+5, 'Average', format_data_header)
        worksheet.write_string(row, col+6, '1 Month', format_data_header)
        worksheet.write_string(row, col+7, '2 Month', format_data_header)
        worksheet.write_string(row, col+8, '3 Month', format_data_header)
        worksheet.write_string(row, col+9, '4 Month', format_data_header)
        worksheet.write_string(row, col+10, '5 Month', format_data_header)
        worksheet.write_string(row, col+11, '6 Month', format_data_header)

        row += 1

        prod_list = []
        if wizard_data.product_ids:
            prod_list = wizard_data.product_ids.ids
        else:
            for order in sale_records:
                if order.product_id.id not in prod_list:
                    prod_list.append(order.product_id.id)

        for prod in prod_list:
            purchase_qty = self.env['purchase.order.line'].search([
                ('state', 'in', ['draft', 'purchase']),
                ('product_id', '=', prod),
            ])
            sale_qty = self.env['sale.order.line'].search([
                ('state', '=', 'sale'),
                ('product_id', '=', prod),
                ('order_id.date_order', '>=', start_date),
                ('order_id.date_order', '<=', end_date),
            ])
            sale_quant = 0.0
            count = 0
            for sale in sale_qty:
                if sale.qty_invoiced:
                    count += 1
                    sale_quant += sale.qty_invoiced
            pur_qty = 0.0
            if purchase_qty:
                for rec in purchase_qty:
                    if rec.order_id.state == 'purchase':
                        for pick in rec.order_id.picking_ids:
                            if pick.state == 'assigned':
                                for line in pick.move_ids_without_package:
                                    if line.product_id.id == rec.product_id.id:
                                        pur_qty += line.product_uom_qty
                    if rec.state == 'draft':
                        pur_qty += rec.product_qty
            product_rec = self.env['product.product'].search([
                ('id', '=', prod),
            ])

            total = product_rec.virtual_available + pur_qty
            average = sale_quant/int(wizard_data.avg_period)
            new_value = total - average

            worksheet.write_string(row, col, product_rec.name or '', format_data_left)
            worksheet.write_string(row, col+1, product_rec.categ_id.name or '', format_data_left)
            worksheet.write_number(row, col+2, product_rec.virtual_available, format_data_right)
            worksheet.write_number(row, col+3, pur_qty, format_data_right)
            worksheet.write_number(row, col+4, total, format_data_right)
            worksheet.write_number(row, col+5, average, format_data_right)
            if new_value < 0:
                worksheet.write_number(row, col+6, new_value, format_data_right_red)
            else:
                worksheet.write_number(row, col+6, new_value, format_data_right)
            new_value -= average
            if new_value < 0:
                worksheet.write_number(row, col+7, new_value, format_data_right_red)
            else:
                worksheet.write_number(row, col+7, new_value, format_data_right)
            new_value -= average
            if new_value < 0:
                worksheet.write_number(row, col+8, new_value, format_data_right_red)
            else:
                worksheet.write_number(row, col+8, new_value, format_data_right)
            new_value -= average
            if new_value < 0:
                worksheet.write_number(row, col+9, new_value, format_data_right_red)
            else:
                worksheet.write_number(row, col+9, new_value, format_data_right)
            new_value -= average
            if new_value < 0:
                worksheet.write_number(row, col+10, new_value, format_data_right_red)
            else:
                worksheet.write_number(row, col+10, new_value, format_data_right)
            new_value -= average
            if new_value < 0:
                worksheet.write_number(row, col+11, new_value, format_data_right_red)
            else:
                worksheet.write_number(row, col+11, new_value, format_data_right)
            row += 1
