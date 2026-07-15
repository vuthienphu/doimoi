# Quy trinh kiem thu dcg_custom_crm

Tai lieu nay dung de test module `dcg_custom_crm` sau khi install hoac upgrade tren Odoo 19.

## 1. Dieu kien truoc khi test

- Odoo dang chay tren port dang dung, vi du `http://localhost:8070`.
- Database da cai cac module phu thuoc: `crm`, `project`, `mail`, `contacts`.
- Module `dcg_custom_crm` da duoc install hoac upgrade.
- User test co quyen CRM va Sales Manager neu can test dong bo hoa hong team.

## 2. Upgrade module truoc khi test

Thao tac tren UI:

1. Vao `Apps`.
2. Tim `DCG Custom CRM`.
3. Bam `Upgrade`.
4. Refresh browser bang `Ctrl + F5`.

Neu vua sua theme `muk_web_theme`, upgrade them module `MuK Backend Theme` va refresh lai trinh duyet.

## 3. Test Sales Team Commission

Duong dan:

```text
CRM > Cau hinh > Bo phan sales
```

Test case TC-CRM-001: Hien thi hoa hong tren Sales Team

Buoc thuc hien:

1. Mo mot Sales Team.
2. Kiem tra field `Phan tram hoa hong (%)`.
3. Nhap gia tri `5`.
4. Luu record.

Ket qua mong doi:

- Field hien thi dung tren form Sales Team.
- Gia tri luu duoc.

Test case TC-CRM-002: Hoa hong thanh vien mac dinh theo team

Buoc thuc hien:

1. Tren Sales Team dang co `Phan tram hoa hong (%) = 5`.
2. Them mot thanh vien moi.
3. Mo form thanh vien vua them.

Ket qua mong doi:

- Thanh vien co field `Phan tram hoa hong (%)`.
- Gia tri mac dinh bang `5`.

Test case TC-CRM-003: Sua hoa hong team khong tu dong cap nhat thanh vien

Buoc thuc hien:

1. Sua hoa hong cua mot thanh vien thanh `3`.
2. Quay lai Sales Team.
3. Sua hoa hong team thanh `7`.
4. Luu.
5. Kiem tra lai thanh vien.

Ket qua mong doi:

- Hoa hong thanh vien van la `3`.
- He thong khong tu dong dong bo khi chi sua field tren team.

Test case TC-CRM-004: Dong bo hoa hong bang button

Buoc thuc hien:

1. Tren Sales Team, bam `Cap nhat toan bo hoa hong`.
2. Wizard hien ra.
3. Bam `Xac nhan`.
4. Kiem tra lai danh sach thanh vien.
5. Kiem tra chatter cua Sales Team.

Ket qua mong doi:

- Toan bo thanh vien cua team hien tai duoc cap nhat hoa hong bang hoa hong team.
- Team khac khong bi anh huong.
- Chatter co log so luong thanh vien da cap nhat.
- UI hien notification thanh cong.

## 4. Test Opportunity Commission

Duong dan:

```text
CRM > Ban hang > Pipeline
```

Test case TC-CRM-005: Hien thi hoa hong tren Opportunity

Buoc thuc hien:

1. Mo mot Opportunity.
2. Chon `Sales Team`.
3. Chon `Salesperson` la thanh vien cua team.
4. Kiem tra field `Phan tram hoa hong (%)`.

Ket qua mong doi:

- Field readonly.
- Gia tri bang hoa hong cua `crm.team.member` tuong ung voi `team_id` va `user_id`.

## 5. Test quy trinh Khao sat

Test case TC-CRM-006: Hoan thanh khao sat

Buoc thuc hien:

1. Mo Opportunity chua khao sat.
2. Bam `Hoan thanh khao sat`.
3. Mo tab `Khao sat`.
4. Kiem tra chatter.

Ket qua mong doi:

- `Da khao sat` duoc check.
- `Ngay hoan thanh khao sat` co gia tri.
- Chatter co log `Da hoan thanh khao sat ngay ...`.
- Button doi sang `Tiep tuc khao sat`.

Test case TC-CRM-007: Tiep tuc khao sat

Buoc thuc hien:

1. Bam `Tiep tuc khao sat`.
2. Nhap `Noi dung`.
3. Nhap `Tu ngay`.
4. Nhap `Den ngay` lon hon hoac bang `Tu ngay`.
5. Bam `Xac nhan`.

Ket qua mong doi:

- Wizard dong lai.
- Chatter co log `Khao sat them: ... - Tu ... den ...`.
- `Da khao sat` van giu True.

Test case TC-CRM-008: Validate ngay khao sat

Buoc thuc hien:

1. Bam `Tiep tuc khao sat`.
2. Nhap `Den ngay` nho hon `Tu ngay`.
3. Bam `Xac nhan`.

Ket qua mong doi:

- He thong bao loi validation.
- Wizard khong ghi chatter.

## 6. Test quy trinh Demo

Test case TC-CRM-009: Hoan thanh demo

Buoc thuc hien:

1. Mo Opportunity chua demo.
2. Bam `Hoan thanh demo`.
3. Mo tab `Demo`.
4. Kiem tra chatter.

Ket qua mong doi:

- `Da demo` duoc check.
- `Ngay hoan thanh demo` co gia tri.
- Chatter co log `Da hoan thanh demo ngay ...`.
- Button doi sang `Tiep tuc demo`.

Test case TC-CRM-010: Tiep tuc demo

Buoc thuc hien:

1. Bam `Tiep tuc demo`.
2. Nhap noi dung demo them.
3. Nhap khoang ngay hop le.
4. Bam `Xac nhan`.

Ket qua mong doi:

- Chatter co log `Demo them: ... - Tu ... den ...`.
- `Da demo` van giu True.

## 7. Test tab Khao sat va Demo

Test case TC-CRM-011: Luu thong tin bo sung

Buoc thuc hien:

1. Mo tab `Khao sat`.
2. Nhap `Ghi chu khao sat`.
3. Them lien he vao `Nguoi lien he khac`.
4. Mo tab `Demo`.
5. Upload file vao `File uoc tinh cong viec`.
6. Luu Opportunity.

Ket qua mong doi:

- Ghi chu luu duoc.
- File dinh kem luu duoc.
- `Nguoi lien he khac` chi cho chon contact ca nhan, khong phai cong ty.

## 8. Test tu dong tao Project khi Won

Test case TC-CRM-012: Tao Project khi Opportunity Won

Buoc thuc hien:

1. Mo Opportunity chua co `Link du an`.
2. Bam `Won` hoac keo Opportunity sang cot `Won`.
3. Mo lai Opportunity.
4. Kiem tra field `Link du an`.
5. Mo Project vua tao.
6. Kiem tra chatter Opportunity.

Ket qua mong doi:

- Project duoc tao tu dong.
- `Link du an` tren Opportunity duoc gan.
- Project co:
  - `name = ten Opportunity`
  - `partner_id = customer cua Opportunity`
  - `user_id = salesperson cua Opportunity`
  - `x_lead_id = id Opportunity`
- Chatter co log `Du an [ten project] da duoc tao lien ket voi Co hoi nay.`

Test case TC-CRM-013: Khong tao trung Project

Buoc thuc hien:

1. Opportunity da co `Link du an`.
2. Chuyen Opportunity tu Won ve mot stage xu ly, sau do set Won lai.
3. Kiem tra danh sach Project.

Ket qua mong doi:

- Khong tao them Project trung.

Test case TC-CRM-014: Co san Link du an thi khong tao Project moi

Buoc thuc hien:

1. Mo Opportunity chua Won.
2. Chon san mot Project vao field `Link du an`.
3. Set Opportunity Won.
4. Kiem tra danh sach Project.

Ket qua mong doi:

- He thong khong tao Project moi.
- Opportunity giu nguyen `Link du an` da chon.

## 9. Test List View Opportunity

Test case TC-CRM-015: Cot custom tren list

Buoc thuc hien:

1. Vao Pipeline.
2. Chuyen sang List View.
3. Kiem tra cac cot sau `Expected Revenue`.

Ket qua mong doi:

- Co cot `Phan tram hoa hong (%)`.
- Co cot `Link du an`.

## 10. Checklist nghiem thu nhanh

- [ ] Module install/upgrade khong loi.
- [ ] Sales Team co field hoa hong.
- [ ] Sales Team co button `Cap nhat toan bo hoa hong`.
- [ ] Thanh vien co field hoa hong rieng.
- [ ] Sua hoa hong team khong tu dong doi thanh vien.
- [ ] Button dong bo cap nhat dung thanh vien trong team hien tai.
- [ ] Opportunity hien hoa hong readonly.
- [ ] Hoan thanh khao sat ghi flag, datetime va chatter.
- [ ] Tiep tuc khao sat mo wizard va ghi chatter.
- [ ] Wizard validate `date_to >= date_from`.
- [ ] Hoan thanh demo ghi flag, datetime va chatter.
- [ ] Tiep tuc demo mo wizard va ghi chatter.
- [ ] Tab `Khao sat` luu duoc ghi chu va lien he khac.
- [ ] Tab `Demo` luu duoc file uoc tinh cong viec.
- [ ] Won Opportunity tu tao Project.
- [ ] Opportunity co san `Link du an` thi Won khong tao Project moi.
- [ ] Opportunity da co Project thi khong tao trung.
- [ ] List View Opportunity co cot custom.

## 11. Xu ly loi thuong gap

Khong thay field/button moi:

1. Upgrade module `dcg_custom_crm`.
2. Refresh browser bang `Ctrl + F5`.
3. Kiem tra user co quyen phu hop.

App switcher bi chu trang tren nen trang:

1. Upgrade module `muk_web_theme`.
2. Refresh browser bang `Ctrl + F5`.
3. Neu van con, bat developer mode va clear assets trong menu debug.

Button dong bo hoa hong khong hien:

1. Kiem tra user co group `Sales Manager`.
2. Upgrade module `dcg_custom_crm`.
3. Mo lai form Sales Team.
