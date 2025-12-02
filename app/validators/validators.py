# app/validators/validators.py
from app.core.base_validator import BaseValidator
from app.utils.date_utils import parse_date, months_between, days_between
from app.utils.fuzzy_matcher import fuzzy_ratio, normalize_string

# All validators follow evaluate(rule, context, resolver) -> returns dict result

class LTVValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        ltv = resolver.resolve(context, 'los', 'ltv')
        cltv = resolver.resolve(context, 'los', 'cltv')
        hcltv = resolver.resolve(context, 'los', 'hcltv')
        thresholds = rule.get('thresholds', {})
        details = {'ltv': ltv, 'cltv': cltv, 'hcltv': hcltv, 'thresholds': thresholds}
        def to_pct(x):
            if x is None:
                return None
            try:
                v = float(x)
                if v <= 1:
                    v = v * 100
                return v
            except:
                return None
        l = to_pct(ltv)
        c = to_pct(cltv)
        h = to_pct(hcltv)
        if thresholds:
            if l is not None and thresholds.get('ltv') is not None and l > thresholds.get('ltv'):
                return self.alert_result(rule, details=details)
            if c is not None and thresholds.get('cltv') is not None and c > thresholds.get('cltv'):
                return self.alert_result(rule, details=details)
            if h is not None and thresholds.get('hcltv') is not None and h > thresholds.get('hcltv'):
                return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class DTIValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        dti = resolver.resolve(context, 'los', 'dti')
        params = rule.get('params', {})
        limit = params.get('dti_limit', 50)
        details = {'dti': dti, 'limit': limit}
        try:
            d = float(dti)
        except:
            return self.not_applicable_result(rule)
        if d > limit:
            return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class OccupancyValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 14: For HomeReady/Home Possible -> property_will_be must be Primary
        prop = resolver.resolve(context, 'los', 'property_will_be')
        details = {'property_will_be': prop}
        if prop is None or prop == "":
            return self.not_applicable_result(rule)
        if str(prop).strip().lower() != 'primary':
            return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class SecondHomeValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 15: if Property Will Be Secondary -> No Units must equal 1
        no_units = resolver.resolve(context, 'los', 'no_units')
        details = {'no_units': no_units}
        try:
            if int(no_units) != 1:
                return self.alert_result(rule, details=details)
        except:
            return self.not_applicable_result(rule)
        return self.pass_result(rule, details=details)

class InvestmentValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 16: Investment property not manufactured
        loan_prog = resolver.resolve(context, 'los', 'loan_program_detail')
        prop_type = resolver.resolve(context, 'los', 'property_type')
        details = {'loan_program_detail': loan_prog, 'property_type': prop_type}
        if loan_prog and 'manufactured' in str(loan_prog).lower():
            return self.alert_result(rule, details=details)
        if prop_type and 'manufactured' in str(prop_type).lower():
            return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class CreditScoreValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 17: Average representative > 620
        score = resolver.resolve(context, 'los', 'average_representative_credit_score')
        details = {'score': score}
        try:
            s = float(score)
        except:
            return self.not_applicable_result(rule)
        if s <= 620:
            return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class GiftValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 18: CONDITION only if gift amount > 0 (or cash_to_borrower positive)
        gift_amount = resolver.resolve(context, 'los', 'gift_amount')
        cash_to = resolver.resolve(context, 'los', 'cash_to_borrower')
        details = {'gift_amount': gift_amount, 'cash_to_borrower': cash_to}
        try:
            g = float(gift_amount) if gift_amount is not None else 0.0
        except:
            g = 0.0
        try:
            c = float(cash_to) if cash_to is not None else 0.0
        except:
            c = 0.0
        if g > 0 or c > 0:
            return self.condition_result(rule, message=rule.get('alert_message'), details=details)
        return self.pass_result(rule, details=details)

class CashoutSeasoningValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 19: Two-step matching
        # Step (i): liabilities account last4 + name fuzzy match with tradelines
        # Step (ii): if (i) pass, check seasoning months > 12 between tradeline date opened & estimated closing
        liabilities_acc = resolver.resolve(context, 'los', 'liabilities_account_number') or ""
        liabilities_name = resolver.resolve(context, 'los', 'liabilities_name') or ""
        est_close = resolver.resolve(context, 'los', 'estimated_closing_date')
        credit = context.get('credit_report', {})
        details = {'liabilities_account_number': liabilities_acc, 'liabilities_name': liabilities_name, 'estimated_closing_date': est_close}
        tradelines = []
        if isinstance(credit, dict):
            tradelines = resolver = credit.get('Tradelines') or credit.get('tradelines') or credit.get('TradeLines') or []
        matched = None
        if not tradelines:
            return self.not_applicable_result(rule)
        last4 = str(liabilities_acc)[-4:] if liabilities_acc else ""
        for t in tradelines:
            # standard keys: Creditor_Account_Number, Creditor_Name, Date_Opened
            accno = str(t.get('Creditor_Account_Number', '') or t.get('AccountNumber', '') or t.get('Account_Number', ''))
            acc_last4 = accno[-4:] if accno else ""
            creditor_name = t.get('Creditor_Name') or t.get('Creditor') or t.get('CreditorName') or ""
            if last4 and acc_last4 and last4 == acc_last4:
                score = fuzzy_ratio(creditor_name, liabilities_name)
                details.update({'matched_account_last4': acc_last4, 'creditor_name': creditor_name, 'fuzzy_score': score})
                if score >= rule.get('params', {}).get('name_match_threshold', 70):
                    matched = t
                    break
        if not matched:
            return self.alert_result(rule, message="The mortgage being paid off is not reported on credit report  please review reasoning requirement.", details=details)
        # Step (ii)
        date_opened = matched.get('Date_Opened') or matched.get('OpenedDate') or matched.get('DateOpened')
        if not date_opened or not est_close:
            return self.not_applicable_result(rule)
        try:
            months = months_between(parse_date(date_opened), parse_date(est_close))
        except:
            return self.not_applicable_result(rule)
        if months <= rule.get('params', {}).get('seasoning_months', 12):
            return self.alert_result(rule, message="The seasoning requirement for cash out refinance is not met, review and proceed", details=details)
        return self.pass_result(rule, details=details)

class TitleValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 20: chain title date vs estimated closing >= 6 months
        chain_date = resolver.resolve(context, 'title', 'chain_title_date')
        est_close = resolver.resolve(context, 'los', 'estimated_closing_date')
        details = {'chain_title_date': chain_date, 'estimated_closing_date': est_close}
        if not chain_date or not est_close:
            return self.not_applicable_result(rule)
        try:
            months = months_between(parse_date(chain_date), parse_date(est_close))
        except:
            return self.not_applicable_result(rule)
        if months < rule.get('params', {}).get('min_months', 6):
            return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class FraudValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 21: only when drive report address EXACT matches subject property address
        drive = context.get('drive_report', {})
        est_close = resolver.resolve(context, 'los', 'estimated_closing_date')
        # get drive address components via resolver (fields.yaml)
        dr_street = resolver.resolve(context, 'drive_report', 'drive_street')
        dr_city = resolver.resolve(context, 'drive_report', 'drive_city')
        dr_state = resolver.resolve(context, 'drive_report', 'drive_state')
        dr_unit = resolver.resolve(context, 'drive_report', 'drive_unit')
        # subject property address - using current_address_housing expected to be dict with Street/City/State/Unit
        subj_addr = resolver.resolve(context, 'los', 'current_address_housing') or {}
        subj_street = (subj_addr.get('Street') if isinstance(subj_addr, dict) else subj_addr) or ""
        subj_city = (subj_addr.get('City') if isinstance(subj_addr, dict) else "") or ""
        subj_state = (subj_addr.get('State') if isinstance(subj_addr, dict) else "") or ""
        subj_unit = (subj_addr.get('Unit') if isinstance(subj_addr, dict) else "") or ""
        details = {'drive_addr': {'street': dr_street, 'city': dr_city, 'state': dr_state, 'unit': dr_unit},
                   'subject_addr': {'street': subj_street, 'city': subj_city, 'state': subj_state, 'unit': subj_unit}}
        # exact normalized comparison
        if normalize_string(dr_street) != normalize_string(subj_street) or \
           normalize_string(dr_city) != normalize_string(subj_city) or \
           normalize_string(dr_state) != normalize_string(subj_state) or \
           normalize_string(dr_unit) != normalize_string(subj_unit):
            # if not exact match, rule not applicable
            return self.not_applicable_result(rule)
        # check fraud recorded date vs estimated closing date
        fraud_date = resolver.resolve(context, 'drive_report', 'fraud_recorded_date')
        if not fraud_date or not est_close:
            return self.not_applicable_result(rule)
        try:
            months = months_between(parse_date(fraud_date), parse_date(est_close))
        except:
            return self.not_applicable_result(rule)
        if months < rule.get('params', {}).get('max_months', 6):
            return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class AppraisalPriorSaleValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        prior_sale = resolver.resolve(context, 'appraisal', 'prior_sale_date')
        est_close = resolver.resolve(context, 'los', 'estimated_closing_date')
        details = {'prior_sale_date': prior_sale, 'estimated_closing_date': est_close}
        if not prior_sale or not est_close:
            return self.not_applicable_result(rule)
        try:
            months = months_between(parse_date(prior_sale), parse_date(est_close))
        except:
            return self.not_applicable_result(rule)
        if months < rule.get('params', {}).get('min_months', 6):
            return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class LoanProgramValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 23: HomeReady/Home Possible must be Fixed Rate amortization
        amort = resolver.resolve(context, 'los', 'amortization_type')
        details = {'amortization_type': amort}
        if not amort:
            return self.not_applicable_result(rule)
        if str(amort).strip().lower() not in ['fixed rate', 'fixed']:
            return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class CashbackValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 24: Negative cash from/to borrower must not exceed max(1% loan amount, $2000)
        cash_from = resolver.resolve(context, 'los', 'cash_from_borrower')
        cash_to = resolver.resolve(context, 'los', 'cash_to_borrower')
        loan_amount = resolver.resolve(context, 'los', 'loan_amount')
        details = {'cash_from': cash_from, 'cash_to': cash_to, 'loan_amount': loan_amount}
        try:
            loan = float(loan_amount)
        except:
            return self.not_applicable_result(rule)
        negs = []
        for v in [cash_from, cash_to]:
            try:
                if v is None:
                    continue
                val = float(v)
                if val < 0:
                    negs.append(abs(val))
            except:
                continue
        if not negs:
            return self.pass_result(rule, details=details)
        max_allowed = max(rule.get('params', {}).get('absolute_limit', 2000),
                          loan * rule.get('params', {}).get('percent_limit', 0.01))
        for amt in negs:
            if amt > max_allowed:
                return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class HomebuyerProgramValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 25: Condition if homebuyer education certificate missing
        cert = resolver.resolve(context, 'los', 'homebuyer_education_certificate')
        details = {'homebuyer_education_certificate': cert}
        if cert and str(cert).strip().lower() in ['yes', 'y', 'true']:
            return self.pass_result(rule, details=details)
        return self.condition_result(rule, message=rule.get('condition_message'), details=details)

class HomebuyerLTVValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 26: If LTV > 95 and first-time buyer indicators then condition if certificate missing
        ltv = resolver.resolve(context, 'los', 'ltv')
        cert = resolver.resolve(context, 'los', 'homebuyer_education_certificate')
        details = {'ltv': ltv, 'homebuyer_education_certificate': cert}
        try:
            lp = float(ltv)
            if lp <= 1:
                lp = lp * 100
        except:
            return self.not_applicable_result(rule)
        if lp > rule.get('params', {}).get('max_ltv', 95):
            if cert and str(cert).strip().lower() in ['yes', 'y', 'true']:
                return self.pass_result(rule, details=details)
            return self.condition_result(rule, message=rule.get('condition_message'), details=details)
        return self.pass_result(rule, details=details)

class IncomeValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 27: Compare total_income to area median income (AMI)
        income = resolver.resolve(context, 'los', 'total_income')
        ami = resolver.resolve(context, 'los', 'area_median_income') or rule.get('params', {}).get('area_median_income')
        details = {'total_income': income, 'area_median_income': ami}
        try:
            inc = float(income)
            ami_v = float(ami)
        except:
            return self.not_applicable_result(rule)
        if inc > ami_v:
            return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)

class LienPayoffValidator(BaseValidator):
    def evaluate(self, rule, context, resolver):
        # Rule 28: If liabilities will be paid off -> if count > 1 OR account type != 'Mortgage' -> ALERT
        paid_off = resolver.resolve(context, 'los', 'liabilities_will_be_paid_off')
        acc_type = resolver.resolve(context, 'los', 'liabilities_account_type')
        liab_names = resolver.resolve(context, 'los', 'liabilities_name') or ""
        details = {'paid_off': paid_off, 'account_type': acc_type, 'liabilities_name': liab_names}
        if str(paid_off).strip().lower() in ['yes', 'true']:
            count = 0
            if isinstance(liab_names, str) and liab_names.strip():
                # assume comma separated names
                count = len([x for x in liab_names.split(',') if x.strip()])
            if count > 1:
                return self.alert_result(rule, details=details)
            if not acc_type or 'mortgage' not in str(acc_type).lower():
                return self.alert_result(rule, details=details)
        return self.pass_result(rule, details=details)
