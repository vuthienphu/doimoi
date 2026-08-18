import re
with open('d:/doimoi/dcg_custom_crm/views/res_partner_views.xml', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'<separator string="5\. Sản phẩm / Dịch vụ đang sử dụng"/>.*?</page>'

new_xml = '''<separator string="5. Sản phẩm / Dịch vụ đang sử dụng"/>
                    <field name="account_product_status_ids" nolabel="1" colspan="2">
                        <list editable="bottom">
                            <field name="name"/>
                            <field name="status"/>
                            <field name="project_id"/>
                            <field name="notes"/>
                        </list>
                    </field>

                    <separator string="6. Cơ hội Bán thêm / Bán chéo (Upsell / Cross-sell)"/>
                    <field name="account_upsell_ids" nolabel="1" colspan="2">
                        <list editable="bottom" decoration-success="state==\\'converted\\'" decoration-muted="state==\\'lost\\'">
                            <field name="type"/>
                            <field name="product_name"/>
                            <field name="expected_revenue"/>
                            <field name="currency_id" column_invisible="1"/>
                            <field name="expected_date"/>
                            <field name="user_id"/>
                            <field name="state"/>
                            <field name="opportunity_id" readonly="1" invisible="not opportunity_id"/>
                            <button name="action_create_opportunity" type="object" string="Tạo Cơ hội CRM" icon="fa-plus-circle" invisible="state != \\'qualified\\' or opportunity_id"/>
                        </list>
                    </field>
                </page>'''

content = re.sub(pattern, new_xml, content, flags=re.DOTALL)

with open('d:/doimoi/dcg_custom_crm/views/res_partner_views.xml', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
