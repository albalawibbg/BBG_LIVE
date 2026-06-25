from odoo import models


class PayslipRunXlsxReport(models.AbstractModel):
    _name = 'report.af_hr.hr_batch_payslip_template_xlsx'
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
                'fg_color': '#8ea9db',
                'text_wrap': True,
                'font_size': 13,
            })
            bold_gray = workbook.add_format({
                'bold': True,
                'border': True,
                'valign': 'vcenter',
                'fg_color': '#d9d9d9',
                'text_wrap': True,
                'font_size': 13,
            })
            sheet.set_column('A:A', 5)
            sheet.set_column('B:M', 20)
            sheet.set_column('D:D', 28)

            sheet.write(0, 0, 'رقم', bold_gray)
            sheet.write(0, 1, 'هوية المستفيد', bold_blue)
            sheet.write(0, 2, 'الاسم', bold_gray)
            sheet.write(0, 3, 'رقم الحساب', bold_blue)
            sheet.write(0, 4, 'رمز البنك', bold_blue)
            sheet.write(0, 5, 'اجمالى المبلغ', bold_blue)
            sheet.write(0, 6, 'الراتب الاساسي', bold_gray)
            sheet.write(0, 7, 'بدل السكن', bold_gray)
            sheet.write(0, 8, 'دخل أخر', bold_gray)
            sheet.write(0, 9, 'الخصومات', bold_gray)
            sheet.write(0, 10, 'الكفالة', bold_blue)
            sheet.write(0, 11, 'العملة', bold_blue)
            sheet.write(0, 12, 'الحالة', bold_blue)
            line_index = 1
            col_index = 0
            totals = 0
            total_net = 0
            total_wage = 0
            total_all_housing = 0
            total_other = 0
            total_ded = 0
            payslip_ids = batch.slip_ids
            for line in payslip_ids:
                total = sum(line.line_ids.filtered(lambda l: l.category_id.code == 'BASIC').mapped('total')) + sum(
                    line.line_ids.filtered(lambda l: l.salary_rule_id.code == 'HOUALLOW').mapped('total')) + sum(
                    line.line_ids.filtered(lambda l: l.salary_rule_id.code == 'Other').mapped('total')) - sum(
                    line.line_ids.filtered(lambda l: l.category_id.code == 'DED').mapped('total'))
                net = sum(line.line_ids.filtered(lambda l: l.category_id.code == 'NET').mapped('total'))
                acc_number = ''
                if line.employee_id.bank_account_id.acc_number:
                    acc_number = line.employee_id.bank_account_id.acc_number.replace(' ', '')
                sheet.write(line_index, col_index, line_index, bold_gray)
                sheet.write(line_index, col_index + 1, line.employee_id.identification_id, bold_blue)
                sheet.write(line_index, col_index + 2, '{}'.format(line.employee_id.name), bold_gray)
                sheet.write(line_index, col_index + 3, acc_number, bold_blue)
                sheet.write(line_index, col_index + 4, line.employee_id.bank_account_id.bank_id.bic, bold_blue)
                sheet.write(line_index, col_index + 5, net, bold_blue)
                # sheet.write(line_index, col_index + 6, line.contract_id.wage, bold_gray)
                sheet.write(line_index, col_index + 6,
                            sum(line.line_ids.filtered(lambda l: l.category_id.code == 'BASIC').mapped('total')),
                            bold_gray)
                sheet.write(line_index, col_index + 7,
                            sum(line.line_ids.filtered(lambda l: l.salary_rule_id.code == 'HOUALLOW').mapped('total')),
                            bold_gray)
                sheet.write(line_index, col_index + 8,
                            sum(line.line_ids.filtered(lambda l: l.salary_rule_id.code == 'Other').mapped('total')),
                            bold_gray)
                sheet.write(line_index, col_index + 9,
                            sum(line.line_ids.filtered(lambda l: l.category_id.code == 'DED').mapped('total')),
                            bold_gray)
                sheet.write(line_index, col_index + 10, line.employee_id.kafeel_name, bold_blue)
                sheet.write(line_index, col_index + 11, line.employee_id.bank_account_id.currency_id.name, bold_blue)
                sheet.write(line_index, col_index + 12,
                            'Active' if line.employee_id.contract_id.state == "open" else 'Not Active', bold_blue)
                totals = totals + total
                total_net = total_net + net
                total_wage = total_wage + sum(
                    line.line_ids.filtered(lambda l: l.category_id.code == 'BASIC').mapped('total'))
                total_all_housing = total_all_housing + sum(
                    line.line_ids.filtered(lambda l: l.salary_rule_id.code == 'HOUALLOW').mapped('total'))
                total_other = total_other + sum(
                    line.line_ids.filtered(lambda l: l.salary_rule_id.code == 'Other').mapped('total'))
                total_ded = total_ded + sum(
                    line.line_ids.filtered(lambda l: l.category_id.code == 'DED').mapped('total'))
                col_index = 0
                line_index += 1
            sheet.write(line_index, 0, '', bold_gray)
            sheet.write(line_index, 1, '', bold_blue)
            sheet.write(line_index, 2, ' Total - الاجمالي', bold_gray)
            sheet.write(line_index, 3, '', bold_gray)
            sheet.write(line_index, 4, '', bold_gray)
            sheet.write(line_index, 5, total_net, bold_blue)
            sheet.write(line_index, 6, total_wage, bold_gray)
            sheet.write(line_index, 7, total_all_housing, bold_gray)
            sheet.write(line_index, 8, total_other, bold_gray)
            sheet.write(line_index, 9, total_ded, bold_gray)
            sheet.write(line_index, 10, '', bold_blue)
            sheet.write(line_index, 11, '', bold_blue)
            sheet.write(line_index, 12, '', bold_blue)

            sheet.write(line_index + 2, 3, ' اعداد: %s' % batch.create_uid.name, bold)
            sheet.write(line_index + 3, 3, 'Prepared By %s' % batch.create_uid.name, bold)

            sheet.write(line_index + 2, 7, 'مدير الموارد البشرية', bold)
            sheet.write(line_index + 3, 7, 'HR Manager', bold)
