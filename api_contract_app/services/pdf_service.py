import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from supabase import create_client, Client

class PDFService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "https://yeibbhxubwxcswxlopwu.supabase.co")
        self.supabase_key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InllaWJiaHh1Ynd4Y3N3eGxvcHd1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODQyNjcwNiwiZXhwIjoyMDg0MDAyNzA2fQ.XzGT0KmbJYZkhXch0DsfSWD8uKfDvvC-SJdlqA0oJFQ")
        self.supabase_client: Client = create_client(self.supabase_url, self.supabase_key)
        self.logo_path = os.path.join(os.getcwd(), "logo.png")

    def format_currency(self, value):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def get_month_name_br(self, date_str):
        months = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
            5: "maio", 6: "junho", 7: "julho", 8: "agosto",
            9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }
        dt = datetime.fromisoformat(date_str.replace('Z', ''))
        return f"{months[dt.month]} de {dt.year}"

    async def generate_and_upload(self, data):
        user_data = self.supabase_client.table('users').select('*').eq('id', data.userId).single().execute().data
        employee_data = self.supabase_client.table('employees').select('company_id').eq('user_id', data.userId).eq('is_current_employee', True).single().execute().data
        company_data = self.supabase_client.table('companies').select('*').eq('id', employee_data['company_id']).single().execute().data

        principal_amount = data.simulation.principalAmount
        rollover_amount = data.simulation.settledPrincipal
        net_amount = principal_amount - rollover_amount
        first_inst = data.simulation.installments[0]
        total_installments = len(data.simulation.installments)
        
        pdf_buffer = BytesIO()
        pdf_doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(name='CustomJustify', alignment=TA_JUSTIFY, fontSize=9, leading=11))
        styles.add(ParagraphStyle(name='MainTitle', alignment=TA_CENTER, fontSize=12, fontName='Helvetica-Bold', leading=14))
        styles.add(ParagraphStyle(name='ClauseHeader', fontSize=9, fontName='Helvetica-Bold', leading=12, spaceBefore=12))
        styles.add(ParagraphStyle(name='SigStyle', alignment=TA_CENTER, fontSize=8, fontName='Helvetica-Bold', leading=10))

        pdf_elements = []

        if os.path.exists(self.logo_path):
            contract_logo = Image(self.logo_path, height=150, width=150)
            pdf_elements.append(contract_logo)

        pdf_elements.append(Spacer(1, 20))
        pdf_elements.append(Paragraph("CONTRATO PARTICULAR DE EMPRÉSTIMO CONSIGNADO", styles['MainTitle']))
        pdf_elements.append(Spacer(1, 20))

        preamble_text = (
            f"<b>ZÉ EMPRESTA</b>, pessoa jurídica de direito privado, inscrita no CNPJ sob nº 58.236.336/0001-38, "
            f"com sede à Rua Herculano Aquino, numero 47, Pq Turf Club, na cidade de Campos dos Goytacazes / RJ sob o CEP 28015-200, "
            f"neste ato denominada simplesmente <b>“CREDORA”</b>, e <b>{user_data['full_name'].upper()}</b>, "
            f"portador(a) do CPF nº {user_data['tax_id']}, doravante denominado(a) simplesmente <b>“DEVEDOR”</b>, "
            f"Funcionário(a) da empresa <b>{company_data['company_name'].upper()}</b>, inscrita no CNPJ nº {company_data['company_tax_id']}, "
            f"doravante denominada <b>“EMPRESA PARCEIRA”</b>, celebram o presente contrato nas seguintes condições:"
        )
        pdf_elements.append(Paragraph(preamble_text, styles['CustomJustify']))

        pdf_elements.append(Paragraph("CLÁUSULA PRIMEIRA – OBJETO", styles['ClauseHeader']))
        pdf_elements.append(Paragraph(f"O presente contrato tem como objeto o empréstimo financeiro concedido pela CREDORA ao DEVEDOR, no valor de {self.format_currency(principal_amount)}, a ser pago pelo DEVEDOR conforme condições deste contrato.", styles['CustomJustify']))
        
        pdf_elements.append(Paragraph("CLÁUSULA SEGUNDA – CONDIÇÕES DO EMPRÉSTIMO", styles['ClauseHeader']))
        rollover_html = f"<b>Saldo de Refinanciamento:</b> {self.format_currency(rollover_amount)}<br/>" if rollover_amount > 0 else ""
        conditions_text = (
            f"<b>Valor Total do Empréstimo:</b> {self.format_currency(principal_amount)}<br/>"
            f"{rollover_html}<b>Valor Líquido Liberado:</b> {self.format_currency(net_amount)}<br/>"
            f"<b>Juros:</b> taxa mensal fixa de {data.simulation.interestRate}% ao mês.<br/>"
            f"<b>Forma de pagamento:</b> parcelado em {total_installments} parcelas mensais de {self.format_currency(first_inst.totalAmount)}.<br/>"
            f"<b>Custo Efetivo Total (Valor final a ser pago):</b> {self.format_currency(data.simulation.totalPayable)}<br/>"
            f"<b>Primeiro desconto:</b> folha de pagamento referente ao mês de {self.get_month_name_br(first_inst.dueDate)}."
        )
        pdf_elements.append(Paragraph(conditions_text, styles['CustomJustify']))

        clauses = [
            ("CLÁUSULA TERCEIRA – AUTORIZAÇÃO DE DESCONTO CONSIGNADO", "O DEVEDOR autoriza expressamente a EMPRESA PARCEIRA a descontar mensalmente de seu salário o valor referente às parcelas estabelecidas na Cláusula Segunda e repassá-las diretamente à CREDORA até o 10º dia útil do mês subsequente ao desconto."),
            ("CLÁUSULA QUARTA – RESCISÃO CONTRATUAL E QUITAÇÃO ANTECIPADA", "Em caso de rescisão do contrato de trabalho antes da integral quitação, o DEVEDOR autoriza a EMPRESA PARCEIRA a descontar integralmente o saldo devedor das verbas rescisórias. O DEVEDOR poderá antecipar o pagamento, com aplicação de desconto proporcional dos juros futuros."),
            ("CLÁUSULA QUINTA – DIREITO AO ARREPENDIMENTO", "O DEVEDOR terá o prazo de até 7 (sete) dias corridos após a assinatura para exercer o direito de arrependimento, restituindo integralmente o valor recebido, sem aplicação de juros ou multas."),
            ("CLÁUSULA SEXTA – CESSÃO DE CRÉDITO", "O DEVEDOR reconhece que a CREDORA poderá ceder total ou parcialmente o crédito resultante deste contrato a terceiros."),
            ("CLÁUSULA SÉTIMA – CONFIDENCIALIDADE E PROTEÇÃO DE DADOS", "As partes comprometem-se a tratar com confidencialidade todos os dados pessoais, em estrita conformidade com a LGPD (Lei nº 13.709/2018)."),
            ("CLÁUSULA OITAVA – INADIMPLÊNCIA", "Em caso de atraso, será aplicada multa de 2% sobre o valor devido, acrescida de juros moratórios de 1% ao mês, além da possibilidade de inscrição em órgãos de proteção ao crédito."),
            ("CLÁUSULA NONA – FORO", "Fica eleito o foro da comarca de Campos dos Goytacazes/RJ para dirimir eventuais controvérsias decorrentes deste contrato.")
        ]
        for title, content in clauses:
            pdf_elements.append(Paragraph(title, styles['ClauseHeader']))
            pdf_elements.append(Paragraph(content, styles['CustomJustify']))

        pdf_elements.append(Spacer(1, 25))
        pdf_elements.append(Paragraph(f"Campos dos Goytacazes, RJ, {datetime.now().strftime('%d/%m/%Y')}.", styles['CustomJustify']))
        pdf_elements.append(Spacer(1, 40))

        creditor_sig = Table(
            [[Paragraph("ZÉ EMPRESTA – CREDORA<br/><font size='7.5' face='Helvetica'>CNPJ 58.236.336/0001-38</font>", styles['SigStyle'])]],
            colWidths=[180]
        )
        creditor_sig.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 0.8, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))

        debtor_sig = Table(
            [[Paragraph(f"{user_data['full_name'].upper()}<br/><font size='7.5' face='Helvetica'>DEVEDOR - CPF: {user_data['tax_id']}</font>", styles['SigStyle'])]],
            colWidths=[180]
        )
        debtor_sig.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 0.8, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))

        main_sig_table = Table([[creditor_sig, debtor_sig]], colWidths=[230, 230])
        main_sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        pdf_elements.append(main_sig_table)

        pdf_elements.append(Spacer(1, 40))
        pdf_elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        auth_footer = (
            "<b><font color='grey' size='6.5'>AUTENTICAÇÃO DO SISTEMA</font></b><br/>"
            f"<font color='grey' size='6.5'>CONTRATO: {data.loanId.upper()} | USUÁRIO: {data.userId.upper()}</font>"
        )
        pdf_elements.append(Paragraph(auth_footer, ParagraphStyle(name='Footer', alignment=TA_CENTER)))

        pdf_doc.build(pdf_elements)
        pdf_out = pdf_buffer.getvalue()
        
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        storage_path = f"{data.userId}/{data.loanId}/{ts}.pdf"
        self.supabase_client.storage.from_("contracts").upload(path=storage_path, file=pdf_out, file_options={"content-type": "application/pdf"})
        final_url = self.supabase_client.storage.from_("contracts").get_public_url(storage_path)
        self.supabase_client.table("loan_contracts").update({"contract_url": final_url}).eq("id", data.loanId).execute()

        return {"contractUrl": final_url}