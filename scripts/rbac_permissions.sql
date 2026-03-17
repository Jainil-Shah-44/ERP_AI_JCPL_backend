/* =========================================================
   RBAC MANAGEMENT SCRIPT
   Handles:
   - Assign role to user
   - Remove role from user
   - Replace user role
   - Assign permission to role
   - Remove permission from role
   - View RBAC mappings
   ========================================================= */


/* =========================================================
   USER ↔ ROLE MANAGEMENT
   ========================================================= */


/* Assign role to a user */
-- Example: assign MANAGER role to user1

INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM app_user u
JOIN role r ON r.name = 'MANAGER'
WHERE u.username = 'user1'
ON CONFLICT DO NOTHING;



/* Remove role from a user */

DELETE FROM user_role
WHERE user_id = (
    SELECT id FROM app_user WHERE username = 'user1'
)
AND role_id = (
    SELECT id FROM role WHERE name = 'MANAGER'
);



/* Replace role of a user (remove old role and assign new role) */

WITH u AS (
    SELECT id FROM app_user WHERE username = 'user1'
),
r AS (
    SELECT id FROM role WHERE name = 'ADMIN'
)

DELETE FROM user_role
WHERE user_id IN (SELECT id FROM u);

INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id FROM u, r;



/* =========================================================
   ROLE ↔ PERMISSION MANAGEMENT
   ========================================================= */


/* Assign permission to a role */
-- Example: give DEPARTMENT_EDIT to MANAGER

INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON p.code = 'DEPARTMENT_EDIT'
WHERE r.name = 'MANAGER'
ON CONFLICT DO NOTHING;



/* Remove permission from a role */

DELETE FROM role_permission
WHERE role_id = (
    SELECT id FROM role WHERE name = 'MANAGER'
)
AND permission_id = (
    SELECT id FROM permission WHERE code = 'DEPARTMENT_EDIT'
);



/* Assign permission to multiple roles */

INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
JOIN permission p ON p.code = 'DEPARTMENT_EDIT'
WHERE r.name IN ('SUPERADMIN','ADMIN','MANAGER')
ON CONFLICT DO NOTHING;



/* Remove permission from multiple roles */

DELETE FROM role_permission
WHERE role_id IN (
    SELECT id FROM role WHERE name IN ('USER')
)
AND permission_id = (
    SELECT id FROM permission WHERE code = 'DEPARTMENT_EDIT'
);



/* Reset permissions for a role */

DELETE FROM role_permission
WHERE role_id = (
    SELECT id FROM role WHERE name = 'MANAGER'
);



/* =========================================================
   RBAC INSPECTION QUERIES
   ========================================================= */


/* View all roles assigned to users */

SELECT 
u.username,
r.name AS role
FROM user_role ur
JOIN app_user u ON u.id = ur.user_id
JOIN role r ON r.id = ur.role_id
ORDER BY u.username;



/* View permissions assigned to roles */

SELECT 
r.name AS role,
p.code AS permission
FROM role_permission rp
JOIN role r ON r.id = rp.role_id
JOIN permission p ON p.id = rp.permission_id
ORDER BY r.name, p.code;



/* View permissions of a specific role */

SELECT p.code
FROM role_permission rp
JOIN role r ON r.id = rp.role_id
JOIN permission p ON p.id = rp.permission_id
WHERE r.name = 'MANAGER';



/* View roles that have a specific permission */

SELECT r.name
FROM role_permission rp
JOIN role r ON r.id = rp.role_id
JOIN permission p ON p.id = rp.permission_id
WHERE p.code = 'PURCHASE_CREATE';



/* Full RBAC overview (User → Role → Permission) */

SELECT 
u.username,
r.name AS role,
p.code AS permission
FROM app_user u
JOIN user_role ur ON ur.user_id = u.id
JOIN role r ON r.id = ur.role_id
JOIN role_permission rp ON rp.role_id = r.id
JOIN permission p ON p.id = rp.permission_id
ORDER BY u.username, role, permission;