	-- =====================================================================
	-- SEED DATA FOR MEDICAL TRIAGE CHATBOT - 3 DEPARTMENTS
	-- =====================================================================
	-- Tables: symptom_rules, red_flags, quick_reply_rules
	-- Language: Vietnamese
	-- Departments: 
	--   1 = Khoa Tai Mui Hong (ENT)
	--   2 = Khoa San Phu Khoa (OB/GYN)
	--   3 = Khoa Nhi (Pediatrics)
	-- =====================================================================

	USE Chatbot;
	GO

	-- =====================================================================
	-- 1. SYMPTOM_RULES (13 rules)
	-- =====================================================================

	-- Khoa Tai Mui Hong (4 rules)
	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Bệnh Về Tai',
		1,
		N'["đau tai", "ù tài", "chảy mủ tai", "nghe kém", "ẩm ở tai", "nghe không rõ"]',
		7,
		1,
		4,
		N'["Đau một bên hay cả hai?", "Có chảy dịch từ tai không?", "Có tiếng vo ve trong tai không?"]',
		NULL
	);

	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Bệnh Về Mũi',
		1,
		N'["nghẹt mũi", "chảy nước mũi", "sổ mũi", "viêm mũi", "viêm xoang", "chảy máu mũi", "hắt hơi"]',
		7,
		1,
		4,
		N'["Nghẹt mũi bao lâu rồi?", "Có chảy nước mũi không?", "Có cảm thấy đau vùng mũi không?"]',
		NULL
	);

	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Bệnh Về Họng',
		1,
		N'["đau họng", "khan tiếng", "viêm họng", "nuốt đau", "ho", "mất vị"]',
		7,
		1,
		4,
		N'["Đau họng mấy ngày rồi?", "Có khó nuốt không?", "Có ho nhiều không?"]',
		NULL
	);

	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Đau đầu liên quan đến tai mũi họng',
		1,
		N'["đau đầu", "nhức đầu", "đau nữa đầu", "đau vùng trán", "chóng mặt"]',
		5,
		1,
		4,
		N'["Đâu ở vị trí nào trên đầu?", "Có kèm nghẹt mũi hay đau họng không?"]',
		NULL
	);

	-- Khoa San Phu Khoa (4 rules)
	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Vấn đề kinh nguyệt',
		4,
		N'["kinh nguyệt", "trễ kinh", "mất kinh", "rối loạn kinh", "đau bụng kinh", "ra ra máu bất thường"]',
		8,
		1,
		4,
		N'["Chu Kỳ Kinh Nguyệt của bạn thế nào?", "Lần cuối kinh là khi nào?"]',
		NULL
	);

	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Thai sản',
		4,
		N'["mang thai", "có thai", "mang bầu", "thai nghén", "vỡ ói"]',
		9,
		1,
		3,
		N'["Bạn đang mang thai được mấy tuần/tháng?", "Có triệu chứng gì bất thường?"]',
		NULL
	);

	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Bệnh Phụ Khoa',
		4,
		N'["Phụ khoa", "ngứa vùng kín", "ra dịch", "đau vung kín", "viêm âm đạo", "viêm phụ khoa"]',
		7,
		1,
		4,
		N'["Có dịch ra từ âm đạo không?", "Dịch có màu gì, mùi thế nào?"]',
		NULL
	);

	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Đau bụng dưới - Phụ Khoa',
		4,
		N'["đau bụng dưới", "đau hạ vị", "cứng bụng", "đau vùng bụng dưới"]',
		6,
		1,
		4,
		N'["Đau có liên quan đến kinh nguyệt không?", "Có thai hoặc đang mang thai không?"]',
		NULL
	);

	-- Khoa Nhi (5 rules)
	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Sốt ở trẻ em',
		5,
		N'["sốt", "nóng người", "sốt cao", "sốt nhẹ", "hơi ấm", "còn sốt"]',
		9,
		1,
		3,
		N'["Bé mấy tuổi?", "Sốt bao nhiêu độ?", "Bé sốt mấy ngày?"]',
		NULL
	);

	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Ho ở trẻ em',
		5,
		N'["ho", "ho nhiều", "ho khan", "ho có đồm", "khó thở", "thở khó"]',
		8,
		1,
		4,
		N'["Ho bao lâu rồi?", "Bé có khó thở không?", "Ho có đàm xanh hoặc đàm vàng không?"]',
		NULL
	);


	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Phát ban ở trẻ em',
		5,
		N'["phat ban", "nổi mẫn", "nổi nhọt", "ngứa", "da đỏ", "mề đây"]',
		7,
		1,
		4,
		N'["Ban ở vị trí nào?", "Có sốt kèm không?", "Bé có ngứa nhiều không?"]',
		NULL
	);

	INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions, additional_notes)
	VALUES 
	(
		N'Bỏ ăn/ bú ở trẻ em',
		5,
		N'["bỏ ăn", "bỏ bú", "ăn kém", "bé quậy", "khóc nhiều", "li bì"]',
		8,
		1,
		3,
		N'["Bé mấy tuổi ?", "Đã bỏ ăn/bú bao lâu?", "Có sốt hoặc tiêu chảy đi kèm không?"]',
		NULL
	);

	PRINT 'Inserted 12 symptom_rules successfully';
	GO

	-- =====================================================================
	-- 2. RED_FLAGS (5 flags)
	-- =====================================================================

	INSERT INTO red_flags (flag_name, symptom_pattern, esi_level, action, warning_message, recommended_department, age_constraint, description)
	VALUES 
	(
		N'Cấp cứu Thai sản',
		N'{"primary": ["ra máu", "chảy máu", "xuất huyết"], "secondary": ["co thắt", "vỡ ối", "đau bụng dữ dội"], "context": "pregnant"}',
		1,
		N'emergency',
		N'⚠️ CẢNH BÁO KHẨN CẤP: Bạn đang mang thai và có ra máu/chảy máu. Vui lòng đến Cấp cứu Sản khoa ngay lập tức hoặc gọi 115!',
		N'Cấp cứu Sản khoa',
		NULL,
		N'Ra máu khi mang thai - nguy cơ sảy thai hoặc sinh non'
	);

	INSERT INTO red_flags (flag_name, symptom_pattern, esi_level, action, warning_message, recommended_department, age_constraint, description)
	VALUES 
	(
		N'Sốt cao trẻ nhỏ',
		N'{"primary": ["sốt cao", "sốt"], "secondary": ["co giật", "li bì", "bỏ bú", "quấy khóc"], "context": "pediatric"}',
		2,
		N'urgent',
		N'⚠️ KHẨN CẤP: Trẻ em bị sốt cao cần được khám ngay. Vui lòng đưa bé đến Khoa Nhi trong vòng 1-2 giờ.',
		N'Khoa Nhi',
		N'{"max_age": 15}',
		N'Sốt cao ở trẻ em - nguy cơ co giật hoặc nhiễm trùng nặng'
	);

	INSERT INTO red_flags (flag_name, symptom_pattern, esi_level, action, warning_message, recommended_department, age_constraint, description)
	VALUES 
	(
		N'Khó thở nặng trẻ em',
		N'{"primary": ["khó thở", "thở khò", "thở nhanh"], "secondary": ["môi tím", "ngực co rút", "li bì"], "context": "pediatric"}',
		1,
		N'emergency',
		N'⚠️ CẢNH BÁO KHẨN CẤP: Bé có triệu chứng khó thở nặng. Vui lòng gọi 115 hoặc đến Cấp cứu ngay lập tức!',
		N'Cấp cứu',
		N'{"max_age": 15}',
		N'Khó thở nặng ở trẻ em - nguy cơ suy hô hấp'
	);

	INSERT INTO red_flags (flag_name, symptom_pattern, esi_level, action, warning_message, recommended_department, age_constraint, description)
	VALUES 
	(
		N'Đau bụng dữ dội thai sản',
		N'{"primary": ["đau bụng dữ dội", "đau bụng nặng"], "secondary": ["buồn nôn", "chóng mặt"], "context": "pregnant"}',
		2,
		N'urgent',
		N'⚠️ KHẨN CẤP: Bạn đang mang thai và có đau bụng dữ dội. Vui lòng đến Khoa Sản Phụ Khoa trong vòng 2 giờ để khám.',
		N'Khoa Sản Phụ Khoa',
		NULL,
		N'Đau bụng dữ dội khi mang thai cần kiểm tra kịp thời'
	);

	INSERT INTO red_flags (flag_name, symptom_pattern, esi_level, action, warning_message, recommended_department, age_constraint, description)
	VALUES 
	(
		N'Tai biến Tai Mũi Họng',
		N'{"primary": ["khó thở", "thở khò", "sưng họng"], "secondary": ["khàn giọng", "khàn tiếng", "nuốt khó"], "context": ""}',
		1,
		N'emergency',
		N'⚠️ CẢNH BÁO KHẨN CẤP: Triệu chứng của bạn có thể gây nguy hiểm đường thở. Vui lòng gọi 115 hoặc đến Cấp cứu ngay!',
		N'Cấp cứu',
		NULL,
		N'Sưng họng/khó thở - nguy cơ tắc đường thở'
	);

	PRINT 'Inserted 5 red_flags successfully';
	GO

	-- =====================================================================
	-- 3. QUICK_REPLY_RULES (15 rules)
	-- =====================================================================

	-- Missing Info (4 rules)
	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'missing_info',
		N'age',
		N'[{"id": "age_1", "label": "Dưới 15 tuổi", "value": "Tôi dưới 15 tuổi"}, {"id": "age_2", "label": "15-40 tuổi", "value": "Tôi từ 15 đến 40 tuổi"}, {"id": "age_3", "label": "41-65 tuổi", "value": "Tôi từ 41 đến 65 tuổi"}, {"id": "age_4", "label": "Trên 65 tuổi", "value": "Tôi trên 65 tuổi"}]',
		10
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'missing_info',
		N'gender',
		N'[{"id": "gender_1", "label": "Nam", "value": "Tôi là nam"}, {"id": "gender_2", "label": "Nữ", "value": "Tôi là nữ"}]',
		9
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'missing_info',
		N'duration',
		N'[{"id": "dur_1", "label": "Hôm nay", "value": "Mới bắt đầu hôm nay"}, {"id": "dur_2", "label": "1-3 ngày", "value": "Được 1 đến 3 ngày"}, {"id": "dur_3", "label": "Trên 1 tuần", "value": "Đã hơn 1 tuần"}, {"id": "dur_4", "label": "Trên 1 tháng", "value": "Đã hơn 1 tháng"}]',
		8
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'missing_info',
		N'severity',
		N'[{"id": "sev_1", "label": "Nhẹ", "value": "Mức độ nhẹ, chịu được"}, {"id": "sev_2", "label": "Trung bình", "value": "Mức độ trung bình, khó chịu"}, {"id": "sev_3", "label": "Nặng", "value": "Mức độ nặng, rất khó chịu"}, {"id": "sev_4", "label": "Rất nặng", "value": "Rất nặng, không chịu nổi"}]',
		7
	);

	-- Context (2 rules)
	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'context',
		N'pregnant',
		N'[{"id": "preg_1", "label": "Đau co thắt", "value": "Đau bụng co thắt từng cơn"}, {"id": "preg_2", "label": "Ra máu", "value": "Có ra máu âm đạo"}, {"id": "preg_3", "label": "Ra dịch bất thường", "value": "Có ra dịch bất thường"}, {"id": "preg_4", "label": "Thai máy ít", "value": "Thai máy ít hơn bình thường"}]',
		8
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'context',
		N'pediatric',
		N'[{"id": "ped_1", "label": "Quấy khóc nhiều", "value": "Bé quấy khóc nhiều, không nín"}, {"id": "ped_2", "label": "Bỏ ăn/bú", "value": "Bé bỏ ăn, bỏ bú"}, {"id": "ped_3", "label": "Nôn trớ", "value": "Bé nôn trớ nhiều"}, {"id": "ped_4", "label": "Phát ban", "value": "Bé có phát ban trên da"}]',
		8
	);

	-- Symptom (8 rules)
	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'symptom',
		N'tai',
		N'[{"id": "ear_1", "label": "Đau một bên", "value": "Chỉ đau một bên tai"}, {"id": "ear_2", "label": "Đau hai bên", "value": "Đau cả hai bên tai"}, {"id": "ear_3", "label": "Chảy mủ", "value": "Có chảy mủ tai"}, {"id": "ear_4", "label": "Nghe kém", "value": "Nghe kém, nghe không rõ"}]',
		5
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'symptom',
		N'mui',
		N'[{"id": "nose_1", "label": "Nghẹt mũi", "value": "Bị nghẹt mũi"}, {"id": "nose_2", "label": "Chảy nước mũi", "value": "Chảy nước mũi nhiều"}, {"id": "nose_3", "label": "Chảy máu mũi", "value": "Có chảy máu mũi"}, {"id": "nose_4", "label": "Đau vùng mặt", "value": "Đau vùng mặt, gần mũi"}]',
		5
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'symptom',
		N'hong',
		N'[{"id": "throat_1", "label": "Đau họng", "value": "Đau họng, nuốt đau"}, {"id": "throat_2", "label": "Khàn tiếng", "value": "Bị khàn giọng"}, {"id": "throat_3", "label": "Ho", "value": "Ho nhiều"}, {"id": "throat_4", "label": "Soi mảng", "value": "Họng sưng, đỏ mảng"}]',
		5
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'symptom',
		N'sot',
		N'[{"id": "fev_1", "label": "Sốt cao >39°C", "value": "Sốt cao trên 39 độ"}, {"id": "fev_2", "label": "Sốt nhẹ 37-38°C", "value": "Sốt nhẹ khoảng 37-38 độ"}, {"id": "fev_3", "label": "Sốt kèm ho", "value": "Sốt kèm theo ho"}, {"id": "fev_4", "label": "Sốt kèm đau đầu", "value": "Sốt kèm đau đầu"}]',
		5
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'symptom',
		N'kinh nguyet',
		N'[{"id": "mens_1", "label": "Trễ kinh", "value": "Kinh đến trễ"}, {"id": "mens_2", "label": "Rối loạn", "value": "Kinh nguyệt không đều"}, {"id": "mens_3", "label": "Ra máu nhiều", "value": "Ra máu nhiều bất thường"}, {"id": "mens_4", "label": "Đau bụng kinh", "value": "Đau bụng khi có kinh"}]',
		5
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'symptom',
		N'ho',
		N'[{"id": "cough_1", "label": "Ho khan", "value": "Ho khan, không có đờm"}, {"id": "cough_2", "label": "Ho có đờm", "value": "Ho có đờm"}, {"id": "cough_3", "label": "Ho ra máu", "value": "Ho có lẫn máu"}, {"id": "cough_4", "label": "Ho về đêm", "value": "Ho nhiều về đêm"}]',
		5
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'symptom',
		N'dau dau',
		N'[{"id": "head_1", "label": "Đau nửa đầu", "value": "Đau một bên đầu, nửa đầu"}, {"id": "head_2", "label": "Đau cả đầu", "value": "Đau lan khắp cả đầu"}, {"id": "head_3", "label": "Đau kèm buồn nôn", "value": "Đau đầu kèm buồn nôn"}, {"id": "head_4", "label": "Đau khi nhìn sáng", "value": "Đau đầu, khó chịu khi nhìn ánh sáng"}]',
		5
	);

	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'symptom',
		N'phu khoa',
		N'[{"id": "gyn_1", "label": "Ngứa vùng kín", "value": "Ngứa vùng kín"}, {"id": "gyn_2", "label": "Ra dịch", "value": "Có ra dịch bất thường"}, {"id": "gyn_3", "label": "Đau vùng kín", "value": "Đau vùng bên trong"}, {"id": "gyn_4", "label": "Mùi hôi", "value": "Có mùi hôi bất thường"}]',
		5
	);

	-- Default (1 rule)
	INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
	VALUES 
	(
		N'default',
		N'initial',
		N'[{"id": "init_1", "label": "Tai Mũi Họng", "value": "Tôi bị vấn đề về tai, mũi hoặc họng"}, {"id": "init_2", "label": "Sản Phụ Khoa", "value": "Tôi có vấn đề phụ khoa hoặc mang thai"}, {"id": "init_3", "label": "Bệnh trẻ em", "value": "Con tôi bị bệnh, cần khám Nhi khoa"}, {"id": "init_4", "label": "Khác", "value": "Tôi có triệu chứng khác"}]',
		1
	);

	PRINT 'Inserted 15 quick_reply_rules successfully';
	GO

	-- =====================================================================
	-- VERIFICATION
	-- =====================================================================

	PRINT '';
	PRINT '=====================================================================';
	PRINT 'SEED DATA INSERTION COMPLETED';
	PRINT '=====================================================================';
	PRINT 'symptom_rules: 12 rows';
	PRINT 'red_flags: 5 rows';
	PRINT 'quick_reply_rules: 15 rows';
	PRINT '=====================================================================';
	GO

	-- Check counts
	SELECT 'symptom_rules' AS TableName, COUNT(*) AS [RowCount] FROM symptom_rules
	UNION ALL
	SELECT 'red_flags', COUNT(*) FROM red_flags
	UNION ALL
	SELECT 'quick_reply_rules', COUNT(*) FROM quick_reply_rules;
	GO
