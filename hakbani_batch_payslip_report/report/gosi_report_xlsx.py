from odoo import models


class PayslipRunXlsxReport(models.AbstractModel):
    _name = 'report.hakbani_batch_payslip_report.hr_gosi_template_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, batches):
        for batch in batches:
            report_name = batch.name
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({
                'bold': True,
                'border': True,
                'valign': 'vcenter',
                'text_wrap': True,
                'font_size': 14,
            })
            bold_blue = workbook.add_format({
                'bold': True,
                'border': True,
                'valign': 'vcenter',
                'align': 'center',
                'fg_color': '#8ea9db',
                'text_wrap': True,
                'font_size': 11,
            })
            bold_gray = workbook.add_format({
                # 'bold': True,
                'border': True,
                'valign': 'vcenter',
                'align': 'center',
                # 'fg_color': '#d9d9d9',
                'text_wrap': True,
                'font_size': 10,
            })
            sheet.set_column('A:A', 10)
            sheet.set_column('B:C', 35)
            sheet.set_column('D:I', 20)

            sheet.set_row(0, 30)

            sheet.write(0, 0, 'Number', bold_blue)
            sheet.write(0, 1, 'Employee Name', bold_blue)
            sheet.write(0, 2, 'Job Title', bold_blue)
            sheet.write(0, 3, 'Nationality', bold_blue)
            sheet.write(0, 4, 'Gosi Wage', bold_blue)
            sheet.write(0, 5, 'Dangers 2% \n (Company)', bold_blue)
            sheet.write(0, 6, 'Saudi Employee \n 10%', bold_blue)
            sheet.write(0, 7, 'Saudi Employee 10% \n (Company)', bold_blue)
            sheet.write(0, 8, 'Total', bold_blue)

            line_index = 1
            col_index = 0

            total_gosi = 0
            total_gosi_2 = 0
            total_gosi_10 = 0
            total_gosi_10_com = 0
            grand_total = 0

            grand_totals = 0

            payslip_ids = batch.slip_ids
            for line in payslip_ids:
                contract = self.env['hr.contract'].search([('employee_id', '=', line.employee_id.id),
                                                           ('state', '=', 'open')], limit=1)
                gosi = contract.gosiwage if contract else 0
                gosi_2 = sum(line.line_ids.filtered(lambda l: l.code == 'G2').mapped('total'))
                gosi_10 = sum(line.line_ids.filtered(lambda l: l.code == 'G10').mapped('total'))
                gosi_10_com = sum(line.line_ids.filtered(lambda l: l.code == 'GC10').mapped('total'))
                total = gosi + gosi_2 + gosi_10 + gosi_10_com

                sheet.write(line_index, col_index, line_index, bold_gray)
                sheet.write(line_index, col_index + 1, line.employee_id.name or '', bold_gray)
                sheet.write(line_index, col_index + 2, line.employee_id.job_title or '', bold_gray)
                sheet.write(line_index, col_index + 3, line.employee_id.country_id.name or '', bold_gray)
                sheet.write(line_index, col_index + 4, gosi, bold_gray)
                sheet.write(line_index, col_index + 5, gosi_2, bold_gray)
                sheet.write(line_index, col_index + 6, gosi_10, bold_gray)
                sheet.write(line_index, col_index + 7, gosi_10_com, bold_gray)
                sheet.write(line_index, col_index + 8, total, bold_gray)

                line_index += 1

                total_gosi += gosi
                total_gosi_2 += gosi_2
                total_gosi_10 += gosi_10
                total_gosi_10_com += gosi_10_com
                grand_total += total


            sheet.write(line_index, 4, total_gosi, bold_blue)
            sheet.write(line_index, 5, total_gosi_2, bold_blue)
            sheet.write(line_index, 6, total_gosi_10, bold_blue)
            sheet.write(line_index, 7, total_gosi_10_com, bold_blue)
            sheet.write(line_index, 8, grand_total, bold_blue)

            # line_index += 3
            #
            # sheet.write(line_index, 1, 'اعداد', bold)
            # # sheet.write(line_index, 1, 'Prepared By', bold)
            #
            # sheet.write(line_index, 5, 'مدير الموارد البشرية', bold)
            # # sheet.write(line_index, 5, 'HR Manager', bold)
            #
            # sheet.write(line_index, 10, 'المدير المالي', bold)
            # # sheet.write(line_index, 10, 'Finance Manager', bold)
            #
            # sheet.write(line_index, 16, 'الرئيس التنفيذي', bold)
            # # sheet.write(line_index, 15, 'CEO', bold)
