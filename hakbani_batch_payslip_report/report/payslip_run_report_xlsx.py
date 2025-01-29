from odoo import models


class PayslipRunXlsxReport(models.AbstractModel):
    _name = 'report.hakbani_batch_payslip_report.hr_batch_payslip_xlsx'
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
                'font_size': 13,
            })
            bold_gray = workbook.add_format({
                # 'bold': True,
                'border': True,
                'valign': 'vcenter',
                'align': 'center',
                # 'fg_color': '#d9d9d9',
                'text_wrap': True,
                'font_size': 12,
            })
            sheet.set_column('A:A', 5)
            sheet.set_column('B:C', 45)
            sheet.set_column('D:P', 20)
            sheet.set_column('Q:Q', 28)

            sheet.write(0, 0, 'رقم', bold_blue)
            sheet.write(0, 1, 'الاسم / الوظيفة', bold_blue)
            sheet.write(0, 2, 'القسم', bold_blue)
            sheet.write(0, 3, 'ايام العمل', bold_blue)
            sheet.write(0, 4, 'الراتب الاساسي', bold_blue)
            sheet.write(0, 5, 'بدل السكن', bold_blue)
            sheet.write(0, 6, 'بدل النقل', bold_blue)
            sheet.write(0, 7, 'بدل استخدام سيارة', bold_blue)
            sheet.write(0, 8, 'فرق مباشرة العمل', bold_blue)
            sheet.write(0, 9, 'بدلات اخرى', bold_blue)
            sheet.write(0, 10, 'مستحقات ومكافأت', bold_blue)
            sheet.write(0, 11, 'اضافي متغير', bold_blue)
            sheet.write(0, 12, 'اجمالى الراتب', bold_blue)
            sheet.write(0, 13, 'تأمينات اجتماعية', bold_blue)
            sheet.write(0, 14, 'السلف', bold_blue)
            sheet.write(0, 15, 'حسومات أخرى', bold_blue)
            sheet.write(0, 16, 'صافي الراتب', bold_blue)

            sheet.write(1, 0, '', bold_blue)
            sheet.write(1, 1, '', bold_blue)
            sheet.write(1, 2, '', bold_blue)
            sheet.write(1, 3, '', bold_blue)
            sheet.write(1, 4, 'BASIC', bold_blue)
            sheet.write(1, 5, 'HOUALLOW', bold_blue)
            sheet.write(1, 6, 'TRAALLOW', bold_blue)
            sheet.write(1, 7, 'CARALLOW', bold_blue)
            sheet.write(1, 8, 'BAOAE', bold_blue)
            sheet.write(1, 9, 'OTALLOW', bold_blue)
            sheet.write(1, 10, 'BAOA', bold_blue)
            sheet.write(1, 11, 'OTV', bold_blue)
            sheet.write(1, 12, 'GROSS', bold_blue)
            sheet.write(1, 13, 'G10', bold_blue)
            sheet.write(1, 14, 'LOAN', bold_blue)
            sheet.write(1, 15, 'DEDUCTION', bold_blue)
            sheet.write(1, 16, 'NET', bold_blue)


            line_index = 2
            col_index = 0

            total_basic = 0
            total_housing = 0
            total_transportation = 0
            total_car_amount = 0
            total_extra_working_day = 0
            total_other = 0
            total_bonus = 0
            total_overtime = 0
            total_gross = 0
            total_gosi = 0
            total_loan = 0
            total_ded = 0
            total_net = 0

            grand_totals = 0

            payslip_ids = batch.slip_ids
            for line in payslip_ids:
                basic_salary = sum(line.line_ids.filtered(lambda l: l.code == 'BASIC').mapped('total'))
                housing_amount = sum(line.line_ids.filtered(lambda l: l.code == 'HOUALLOW').mapped('total'))
                trans_amount = sum(line.line_ids.filtered(lambda l: l.code == 'TRAALLOW').mapped('total'))
                car_amount = sum(line.line_ids.filtered(lambda l: l.code == 'CARALLOW').mapped('total'))
                extra_working_days = sum(line.line_ids.filtered(lambda l: l.code == 'BAOAE').mapped('total'))
                other_alloc = sum(line.line_ids.filtered(lambda l: l.code == 'OTALLOW').mapped('total'))
                bonus = sum(line.line_ids.filtered(lambda l: l.code == 'BAOA').mapped('total'))
                over_time = sum(line.line_ids.filtered(lambda l: l.code == 'OTV').mapped('total'))
                gross = sum(line.line_ids.filtered(lambda l: l.code == 'GROSS').mapped('total'))
                gosi = sum(line.line_ids.filtered(lambda l: l.code == 'G10').mapped('total'))
                loan = sum(line.line_ids.filtered(lambda l: l.code == 'LOAN').mapped('total'))
                other_ded = sum(line.line_ids.filtered(lambda l: l.code == 'DEDUCTION').mapped('total'))
                net = sum(line.line_ids.filtered(lambda l: l.code == 'NET').mapped('total'))

                worked_days_rec = sum(
                    line.worked_days_line_ids.filtered(lambda p: p.code == 'WORK100').mapped('number_of_days'))

                sheet.write(line_index, col_index, line_index, bold_gray)
                sheet.write(line_index, col_index + 1, line.employee_id.name or '', bold_gray)
                sheet.write(line_index, col_index + 2, line.employee_id.department_id.name or '', bold_gray)
                sheet.write(line_index, col_index + 3, worked_days_rec, bold_gray)
                sheet.write(line_index, col_index + 4, basic_salary, bold_gray)
                sheet.write(line_index, col_index + 5, housing_amount, bold_gray)
                sheet.write(line_index, col_index + 6, trans_amount, bold_gray)
                sheet.write(line_index, col_index + 7, car_amount, bold_gray)
                sheet.write(line_index, col_index + 8, extra_working_days, bold_gray)
                sheet.write(line_index, col_index + 9, other_alloc, bold_gray)
                sheet.write(line_index, col_index + 10, bonus, bold_gray)
                sheet.write(line_index, col_index + 11, over_time, bold_gray)
                sheet.write(line_index, col_index + 12, gross, bold_gray)
                sheet.write(line_index, col_index + 13, gosi, bold_gray)
                sheet.write(line_index, col_index + 14, loan, bold_gray)
                sheet.write(line_index, col_index + 15, other_ded, bold_gray)
                sheet.write(line_index, col_index + 16, net, bold_gray)

                line_index += 1

                total_basic += basic_salary
                total_housing += housing_amount
                total_transportation += trans_amount
                total_car_amount += car_amount
                total_extra_working_day += extra_working_days
                total_other += other_alloc
                total_bonus += bonus
                total_overtime += over_time
                total_gross += gross
                total_gosi += gosi
                total_loan += loan
                total_ded += other_ded
                total_net += net


            grand_totals = total_basic + total_housing + total_transportation + total_extra_working_day + total_other + total_bonus + total_overtime + total_gross + total_gosi + total_loan + total_ded + total_net

            sheet.write(line_index, 4, total_basic, bold_blue)
            sheet.write(line_index, 5, total_housing, bold_blue)
            sheet.write(line_index, 6, total_transportation, bold_blue)
            sheet.write(line_index, 7, total_car_amount, bold_blue)
            sheet.write(line_index, 8, total_extra_working_day, bold_blue)
            sheet.write(line_index, 9, total_other, bold_blue)
            sheet.write(line_index, 10, total_bonus, bold_blue)
            sheet.write(line_index, 11, total_overtime, bold_blue)
            sheet.write(line_index, 12, total_gross, bold_blue)
            sheet.write(line_index, 13, total_gosi, bold_blue)
            sheet.write(line_index, 14, total_loan, bold_blue)
            sheet.write(line_index, 15, total_ded, bold_blue)
            sheet.write(line_index, 16, total_net, bold_blue)

            line_index += 3

            sheet.write(line_index, 1, 'اعداد', bold)
            # sheet.write(line_index, 1, 'Prepared By', bold)

            sheet.write(line_index, 5, 'مدير الموارد البشرية', bold)
            # sheet.write(line_index, 5, 'HR Manager', bold)

            sheet.write(line_index, 10, 'المدير المالي', bold)
            # sheet.write(line_index, 10, 'Finance Manager', bold)

            sheet.write(line_index, 16, 'الرئيس التنفيذي', bold)
            # sheet.write(line_index, 15, 'CEO', bold)
