/* 10th march 2026 */
ALTER TABLE purchase_requisition_item
ADD COLUMN pr_number VARCHAR(50);

ALTER TABLE purchase_requisition_item
ADD COLUMN department_id UUID;

ALTER TABLE purchase_requisition_item
ADD COLUMN department_name VARCHAR(100);

ALTER TABLE purchase_requisition_item
ADD CONSTRAINT fk_pr_item_department
FOREIGN KEY (department_id)
REFERENCES department(id);

UPDATE purchase_requisition_item i
SET pr_number = p.pr_number
FROM purchase_requisition p
WHERE i.pr_id = p.id;



ALTER TABLE raw_material
ADD COLUMN unit_name VARCHAR(50);

UPDATE raw_material rm
SET unit_name = u.unit_code
FROM unit u
WHERE rm.unit_id = u.id;


/* 13 march 2026 */

INSERT INTO permission (code, description) VALUES
('MASTER_VIEW','View all master tables'),

('MASTER_EDIT','Edit all master tables'),

('RAW_MATERIAL_EDIT','Create and edit raw materials'),
('VENDOR_EDIT','Create and edit vendors'),
('CATEGORY_EDIT','Create and edit categories'),
('GROUP_EDIT','Create and edit groups'),
('UNIT_EDIT','Create and edit units'),
('WAREHOUSE_EDIT','Create and edit warehouses'),
('FACTORY_EDIT','Create and edit factories'),

('USER_MANAGE','Create and manage users'),

('PURCHASE_CREATE','Create purchase requisition'),
('PO_APPROVE','Approve purchase orders'),

('GRN_PROCESS','Process goods receipt'),
('INVOICE_MATCH','Match invoices');


INSERT INTO role (name, description) VALUES
('SUPERADMIN','Full system access'),
('ADMIN','System administrator'),
('MANAGER','Procurement manager'),
('USER','Standard system user');


INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON TRUE
WHERE r.name = 'SUPERADMIN';

INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON p.code IN (
'MASTER_VIEW',
'MASTER_EDIT',

'RAW_MATERIAL_EDIT',
'VENDOR_EDIT',
'CATEGORY_EDIT',
'GROUP_EDIT',
'UNIT_EDIT',
'WAREHOUSE_EDIT',
'FACTORY_EDIT',

'USER_MANAGE',

'PURCHASE_CREATE',
'PO_APPROVE',
'GRN_PROCESS',
'INVOICE_MATCH'
)
WHERE r.name = 'ADMIN';

INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON p.code IN (
'MASTER_VIEW',
'MASTER_EDIT',

'RAW_MATERIAL_EDIT',
'VENDOR_EDIT',
'CATEGORY_EDIT',
'GROUP_EDIT',
'UNIT_EDIT',
'WAREHOUSE_EDIT',
'FACTORY_EDIT',

'PURCHASE_CREATE',
'PO_APPROVE',
'GRN_PROCESS'
)
WHERE r.name = 'MANAGER';

INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON p.code IN (
'MASTER_VIEW',

'RAW_MATERIAL_EDIT',
'VENDOR_EDIT',

'PURCHASE_CREATE'
)
WHERE r.name = 'USER';


INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM "app_user" u
JOIN role r ON r.name = 'ADMIN'
WHERE LOWER(u.role) = 'admin';


INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM "app_user" u
JOIN role r ON r.name = 'MANAGER'
WHERE LOWER(u.role) = 'manager';

INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM "app_user" u
JOIN role r ON r.name = 'USER'
WHERE LOWER(u.role) = 'user';

INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM "app_user" u
JOIN role r ON r.name = 'SUPERADMIN'
WHERE LOWER(u.role) IN ('superadmin','super_admin');

/* 15 march 2026 */

INSERT INTO permission (code, description)
VALUES ('DEPARTMENT_EDIT', 'Create and edit departments');

INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON p.code = 'DEPARTMENT_EDIT'
WHERE r.name = 'SUPERADMIN';

INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON p.code = 'DEPARTMENT_EDIT'
WHERE r.name = 'ADMIN';

INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON p.code = 'DEPARTMENT_EDIT'
WHERE r.name = 'MANAGER';


/* 17 march 2026*/

INSERT INTO permission (code, description) VALUES
('PR_CREATE','Create Purchase Requisition'),
('PR_EDIT','Edit Draft PR'),
('PR_SUBMIT','Submit PR'),
('PR_VIEW_OWN','View Own PR'),
('PR_VIEW_ALL','View All PR'),
('PR_APPROVE','Approve PR'),
('PR_REJECT','Reject PR'),

('RFQ_CREATE','Create RFQ'),
('RFQ_INVITE_VENDOR','Invite Vendors to RFQ'),
('RFQ_VIEW','View RFQ'),
('RFQ_COMPARISON','View RFQ Comparison'),
('RFQ_CREATE_PO','Create PO from RFQ')
ON CONFLICT (code) DO NOTHING;


INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON p.code IN (
'PR_CREATE',
'PR_EDIT',
'PR_SUBMIT',
'PR_VIEW_OWN'
)
WHERE r.name = 'USER'
ON CONFLICT DO NOTHING;


INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON p.code IN (
'PR_CREATE',
'PR_EDIT',
'PR_SUBMIT',
'PR_VIEW_OWN',
'PR_VIEW_ALL',
'PR_APPROVE',
'PR_REJECT',
'RFQ_CREATE',
'RFQ_INVITE_VENDOR',
'RFQ_VIEW',
'RFQ_COMPARISON',
'RFQ_CREATE_PO'
)
WHERE r.name IN ('SUPERADMIN','ADMIN','MANAGER')
ON CONFLICT DO NOTHING;



DELETE FROM role_permission
WHERE role_id = (
    SELECT id FROM role WHERE name = 'USER'
)
AND permission_id = (
    SELECT id FROM permission WHERE code = 'VENDOR_EDIT'
);


/* 18 march 2026*/

ALTER TABLE purchase_requisition_attachment
ALTER COLUMN file_path TYPE TEXT;

ALTER TABLE purchase_requisition_attachment
ALTER COLUMN file_type TYPE TEXT;

ALTER TABLE purchase_requisition_attachment
ALTER COLUMN file_name TYPE TEXT;

ALTER TABLE purchase_requisition_item
ADD COLUMN line_number INT;