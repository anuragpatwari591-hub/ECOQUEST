-- EcoQuest Demo/Seed Data
-- Run AFTER schema.sql: mysql -u root -p ecoquest < database/seed.sql
-- Demo account passwords (for viva/demo only, never use in production):
--   student1@ecoquest.com / student123
--   teacher1@ecoquest.com / teacher123
--   admin1@ecoquest.com   / admin123

USE ecoquest;

-- ---------------------------------------------------------------------
-- USERS
-- ---------------------------------------------------------------------
INSERT INTO users (name, email, password_hash, role, class_name, institution, total_xp, current_streak, longest_streak, last_activity_date) VALUES
('Anurag Patwari', 'student1@ecoquest.com', 'scrypt:32768:8:1$fu3ASuTm3tG782gN$2aa54d71345d85d49d4bb2d3e07d16a6fa9aacca17c006e9cf98492f52ace6e248912360f9f7c41ce11336b1311a26dce6c22fb82426fe46f909482b794d88cf', 'student', 'BTech CSE 3rd Year', 'Demo Institute of Technology', 1240, 7, 7, CURDATE()),
('Priya Sharma', 'student2@ecoquest.com', 'scrypt:32768:8:1$fu3ASuTm3tG782gN$2aa54d71345d85d49d4bb2d3e07d16a6fa9aacca17c006e9cf98492f52ace6e248912360f9f7c41ce11336b1311a26dce6c22fb82426fe46f909482b794d88cf', 'student', 'BTech CSE 3rd Year', 'Demo Institute of Technology', 860, 3, 5, CURDATE()),
('Rohit Verma', 'student3@ecoquest.com', 'scrypt:32768:8:1$fu3ASuTm3tG782gN$2aa54d71345d85d49d4bb2d3e07d16a6fa9aacca17c006e9cf98492f52ace6e248912360f9f7c41ce11336b1311a26dce6c22fb82426fe46f909482b794d88cf', 'student', 'BTech CSE 3rd Year', 'Demo Institute of Technology', 430, 1, 2, CURDATE()),
('Mr. Suresh Kumar', 'teacher1@ecoquest.com', 'scrypt:32768:8:1$4DUUsOSwlNU11pxI$b054f702641ab9f1c8154df588ec5f341d20a81e705b3f81fdb91b913d1aba863d43718a229152be6d975b8e5e00c28f95888bdbcfde267ef1ab43e0c3fc34bc', 'teacher', 'BTech CSE 3rd Year', 'Demo Institute of Technology', 0, 0, 0, NULL),
('Admin User', 'admin1@ecoquest.com', 'scrypt:32768:8:1$QLzk8C5rXi5O5ESW$4a7bc7cb139360706831f1235d8d2d9cfb796b10cf6a2cce81414659fd3d7a7f7ee64a4eb48de725d7bd4fd0d132ff1d0e1e8f5afcb663e1bff551e2d68c388e', 'admin', NULL, 'Demo Institute of Technology', 0, 0, 0, NULL);

-- ---------------------------------------------------------------------
-- TOPICS
-- ---------------------------------------------------------------------
INSERT INTO topics (name, description, icon) VALUES
('Climate Change', 'Understand the greenhouse effect, global warming, carbon emissions and how societies can adapt.', '🌍'),
('Pollution', 'Explore air, water, soil and noise pollution and their impact on health and ecosystems.', '🏭'),
('Waste Management', 'Learn about recycling, composting, plastic waste and e-waste handling.', '♻️'),
('Water Conservation', 'Study water scarcity, rainwater harvesting and everyday water-saving practices.', '💧'),
('Renewable Energy', 'Discover solar, wind, hydro and biomass energy as alternatives to fossil fuels.', '⚡'),
('Biodiversity', 'Learn about ecosystems, endangered species and forest conservation.', '🌳');

-- ---------------------------------------------------------------------
-- LESSONS (2 per topic = 12 lessons)
-- ---------------------------------------------------------------------
INSERT INTO lessons (topic_id, title, difficulty, introduction, explanation, key_points, eco_tip, xp_reward) VALUES
(1, 'The Greenhouse Effect', 'Beginner',
 'The greenhouse effect is a natural process that warms the Earth''s surface.',
 'Certain gases in the atmosphere, such as carbon dioxide and methane, trap heat from the sun that would otherwise escape into space. This natural warming keeps Earth habitable, but human activities like burning fossil fuels have increased the concentration of these gases, intensifying the effect and causing global temperatures to rise.',
 'Greenhouse gases trap heat in the atmosphere\nCO2 and methane are major greenhouse gases\nHuman activity has increased greenhouse gas concentration\nThe enhanced greenhouse effect drives global warming',
 'Reduce your carbon footprint by walking, cycling or using public transport for short trips.', 10),
(1, 'Global Warming and Its Effects', 'Intermediate',
 'Global warming refers to the long-term rise in Earth''s average surface temperature.',
 'Rising global temperatures lead to melting glaciers, rising sea levels, more frequent extreme weather events, and disruption of ecosystems. Scientists track these changes using long-term temperature records, satellite data and climate models.',
 'Global warming is a long-term temperature trend\nIt causes melting ice caps and rising sea levels\nExtreme weather events are becoming more frequent\nClimate adaptation strategies help communities cope',
 'Support local reforestation drives — trees absorb CO2 from the atmosphere.', 10),
(2, 'Understanding Air Pollution', 'Beginner',
 'Air pollution occurs when harmful substances are released into the atmosphere.',
 'Air pollution comes from vehicle emissions, industrial processes and burning of fossil fuels. Common pollutants include particulate matter (PM2.5), sulfur dioxide, nitrogen oxides and carbon monoxide, which affect respiratory health and contribute to smog.',
 'Air pollution comes from vehicles, industry and burning fuels\nPM2.5 is a major health-affecting pollutant\nAir Quality Index (AQI) measures pollution levels\nIndoor air quality also matters for health',
 'Avoid burning waste; use exhaust fans and ventilate indoor spaces well.', 10),
(2, 'Water and Soil Pollution', 'Intermediate',
 'Water and soil pollution degrade ecosystems that sustain life.',
 'Water pollution is caused by industrial discharge, agricultural runoff and untreated sewage. Soil pollution results from pesticides, industrial waste and improper disposal of chemicals, reducing soil fertility and contaminating groundwater.',
 'Industrial discharge is a major water pollutant\nAgricultural runoff carries pesticides into water bodies\nSoil pollution reduces fertility over time\nContaminated soil can pollute groundwater',
 'Dispose of chemicals and pesticides responsibly, never down the drain.', 10),
(3, 'Recycling Basics', 'Beginner',
 'Recycling converts waste materials into reusable resources.',
 'Recycling reduces the need for raw materials, saves energy and reduces landfill waste. Common recyclables include paper, glass, metal and certain plastics. Proper segregation at source makes recycling more effective.',
 'Recycling reduces raw material demand\nSegregation at source improves recycling efficiency\nPaper, glass, metal and some plastics are recyclable\nRecycling saves energy compared to producing new materials',
 'Keep separate bins at home for dry and wet waste.', 10),
(3, 'Composting and E-Waste', 'Intermediate',
 'Composting turns organic waste into nutrient-rich soil, while e-waste needs special handling.',
 'Composting decomposes food scraps and garden waste into compost that enriches soil. Electronic waste contains hazardous materials like lead and mercury and must be disposed of through certified e-waste recyclers rather than regular trash.',
 'Composting recycles organic/kitchen waste into fertilizer\nE-waste contains hazardous heavy metals\nE-waste should go to certified recyclers only\nComposting reduces methane emissions from landfills',
 'Start a small compost bin for kitchen vegetable peels at home.', 10),
(4, 'Water Scarcity', 'Beginner',
 'Water scarcity affects millions of people due to overuse and pollution of freshwater sources.',
 'Freshwater makes up a small fraction of Earth''s total water. Population growth, industrial use and pollution are straining available supplies, particularly in regions with low rainfall or poor water infrastructure.',
 'Freshwater is a limited resource\nOveruse and pollution worsen scarcity\nGroundwater levels are declining in many regions\nWater scarcity affects agriculture and daily life',
 'Fix leaking taps promptly — a small drip wastes litres of water daily.', 10),
(4, 'Rainwater Harvesting', 'Intermediate',
 'Rainwater harvesting collects and stores rainwater for later use.',
 'Rainwater harvesting systems capture runoff from rooftops and direct it to storage tanks or recharge pits. This reduces dependence on groundwater and municipal supply while helping recharge local aquifers.',
 'Rainwater harvesting captures rooftop runoff\nStored water can be used for non-drinking purposes\nRecharge pits help replenish groundwater\nIt reduces pressure on municipal water supply',
 'Turn off the tap while brushing your teeth to save water.', 10),
(5, 'Solar and Wind Energy', 'Beginner',
 'Solar and wind are two of the most widely used renewable energy sources.',
 'Solar panels convert sunlight directly into electricity using photovoltaic cells. Wind turbines convert kinetic energy from wind into electricity. Both produce no direct emissions during operation, unlike fossil fuel power plants.',
 'Solar panels use photovoltaic cells to generate electricity\nWind turbines convert wind energy to electricity\nBoth sources produce no operational emissions\nEnergy output depends on weather and location',
 'Switch off lights and appliances when not in use to reduce energy demand.', 10),
(5, 'Hydropower and Biomass', 'Intermediate',
 'Hydropower and biomass are renewable sources that use water flow and organic matter respectively.',
 'Hydropower plants generate electricity from flowing or falling water, typically using dams. Biomass energy comes from burning or converting organic material like agricultural residue and wood waste into fuel or electricity.',
 'Hydropower uses flowing water to generate electricity\nBiomass energy comes from organic material\nBoth are considered renewable when managed sustainably\nDams can also provide flood control and irrigation',
 'Use energy-efficient LED bulbs instead of incandescent bulbs.', 10),
(6, 'Understanding Ecosystems', 'Beginner',
 'An ecosystem is a community of living organisms interacting with their environment.',
 'Ecosystems include producers, consumers and decomposers linked through food chains and food webs. Healthy ecosystems maintain biodiversity, regulate climate and provide resources like clean air, water and food.',
 'Ecosystems connect living organisms and their environment\nFood chains and food webs describe energy flow\nBiodiversity keeps ecosystems resilient\nHuman activity can disrupt ecosystem balance',
 'Plant native species in your garden to support local wildlife.', 10),
(6, 'Endangered Species and Forest Conservation', 'Intermediate',
 'Habitat loss and hunting have pushed many species toward extinction.',
 'Endangered species face threats from deforestation, poaching and climate change. Forest conservation efforts, including protected areas and reforestation, help preserve habitats and the biodiversity they support.',
 'Habitat loss is a leading cause of species endangerment\nProtected areas help conserve biodiversity\nReforestation restores lost forest cover\nConservation requires both policy and community action',
 'Support organizations working on wildlife and forest conservation.', 10);

-- ---------------------------------------------------------------------
-- QUIZZES (one per topic = 6 quizzes)
-- ---------------------------------------------------------------------
INSERT INTO quizzes (topic_id, title, description, created_by) VALUES
(1, 'Climate Change Quiz', 'Test your understanding of the greenhouse effect and global warming.', 4),
(2, 'Pollution Quiz', 'Test your understanding of air, water and soil pollution.', 4),
(3, 'Waste Management Quiz', 'Test your understanding of recycling, composting and e-waste.', 4),
(4, 'Water Conservation Quiz', 'Test your understanding of water scarcity and conservation methods.', 4),
(5, 'Renewable Energy Quiz', 'Test your understanding of solar, wind, hydro and biomass energy.', 4),
(6, 'Biodiversity Quiz', 'Test your understanding of ecosystems and conservation.', 4);

-- ---------------------------------------------------------------------
-- QUESTIONS + OPTIONS (5 per quiz = 30 questions)
-- Quiz 1: Climate Change
-- ---------------------------------------------------------------------
INSERT INTO questions (quiz_id, question_text) VALUES
(1, 'Which gas contributes significantly to the greenhouse effect?'),
(1, 'What is the main cause of the enhanced greenhouse effect?'),
(1, 'Which of these is a direct effect of global warming?'),
(1, 'What is climate adaptation?'),
(1, 'Which sector is a major source of carbon emissions?');

INSERT INTO options (question_id, option_text, is_correct) VALUES
(1, 'Oxygen', FALSE), (1, 'Carbon Dioxide', TRUE), (1, 'Nitrogen', FALSE), (1, 'Hydrogen', FALSE),
(2, 'Volcanic eruptions', FALSE), (2, 'Burning of fossil fuels', TRUE), (2, 'Ocean currents', FALSE), (2, 'Solar flares', FALSE),
(3, 'Cooling oceans', FALSE), (3, 'Melting glaciers and rising sea levels', TRUE), (3, 'Decreasing sea levels', FALSE), (3, 'Reduced rainfall everywhere', FALSE),
(4, 'Ignoring climate risks', FALSE), (4, 'Adjusting practices to cope with climate impacts', TRUE), (4, 'Increasing emissions', FALSE), (4, 'Stopping all industry', FALSE),
(5, 'Fishing', FALSE), (5, 'Transportation and energy production', TRUE), (5, 'Handicrafts', FALSE), (5, 'Local farming only', FALSE);

-- Quiz 2: Pollution
INSERT INTO questions (quiz_id, question_text) VALUES
(2, 'Which pollutant is commonly measured by the Air Quality Index (AQI)?'),
(2, 'What is a major cause of water pollution?'),
(2, 'What does soil pollution primarily reduce?'),
(2, 'Which of these is a source of noise pollution?'),
(2, 'What is smog primarily composed of?');

INSERT INTO options (question_id, option_text, is_correct) VALUES
(6, 'PM2.5 particulate matter', TRUE), (6, 'Pure oxygen', FALSE), (6, 'Water vapor', FALSE), (6, 'Nitrogen gas', FALSE),
(7, 'Industrial discharge and sewage', TRUE), (7, 'Rainfall', FALSE), (7, 'Solar radiation', FALSE), (7, 'Wind', FALSE),
(8, 'Soil fertility', TRUE), (8, 'Soil color', FALSE), (8, 'Soil temperature only', FALSE), (8, 'Soil weight', FALSE),
(9, 'Traffic and industrial machinery', TRUE), (9, 'Birdsong', FALSE), (9, 'Rainfall', FALSE), (9, 'Photosynthesis', FALSE),
(10, 'Smoke and fog combined with pollutants', TRUE), (10, 'Pure clean air', FALSE), (10, 'Ocean spray', FALSE), (10, 'Dust storms only', FALSE);

-- Quiz 3: Waste Management
INSERT INTO questions (quiz_id, question_text) VALUES
(3, 'Which of these materials is commonly recyclable?'),
(3, 'What does composting produce?'),
(3, 'Why must e-waste be handled by certified recyclers?'),
(3, 'What is the first step of effective waste management at home?'),
(3, 'Which gas is released from decomposing organic waste in landfills?');

INSERT INTO options (question_id, option_text, is_correct) VALUES
(11, 'Glass', TRUE), (11, 'Used tissue paper', FALSE), (11, 'Food waste', FALSE), (11, 'Ash', FALSE),
(12, 'Nutrient-rich soil/fertilizer', TRUE), (12, 'Plastic', FALSE), (12, 'Clean drinking water', FALSE), (12, 'Electricity', FALSE),
(13, 'It contains hazardous heavy metals', TRUE), (13, 'It is very heavy', FALSE), (13, 'It has resale value only', FALSE), (13, 'It is biodegradable', FALSE),
(14, 'Segregating dry and wet waste', TRUE), (14, 'Burning all waste', FALSE), (14, 'Mixing all waste together', FALSE), (14, 'Dumping waste in water bodies', FALSE),
(15, 'Methane', TRUE), (15, 'Oxygen', FALSE), (15, 'Helium', FALSE), (15, 'Hydrogen', FALSE);

-- Quiz 4: Water Conservation
INSERT INTO questions (quiz_id, question_text) VALUES
(4, 'What percentage of Earth''s water is easily accessible freshwater? (approx.)'),
(4, 'What does rainwater harvesting help recharge?'),
(4, 'Which of these is a simple household water-saving practice?'),
(4, 'What is a major cause of water scarcity?'),
(4, 'What can rainwater harvesting reduce dependence on?');

INSERT INTO options (question_id, option_text, is_correct) VALUES
(16, 'A very small fraction', TRUE), (16, 'More than half', FALSE), (16, 'Exactly one third', FALSE), (16, 'Almost all of it', FALSE),
(17, 'Groundwater levels', TRUE), (17, 'Ocean salinity', FALSE), (17, 'Air quality', FALSE), (17, 'Soil erosion directly', FALSE),
(18, 'Turning off the tap while brushing teeth', TRUE), (18, 'Leaving taps running', FALSE), (18, 'Washing cars daily with a hose', FALSE), (18, 'Ignoring leaks', FALSE),
(19, 'Overuse and pollution of freshwater sources', TRUE), (19, 'Too much rainfall', FALSE), (19, 'Excess groundwater', FALSE), (19, 'Ocean currents', FALSE),
(20, 'Municipal water supply', TRUE), (20, 'Electricity supply', FALSE), (20, 'Internet bandwidth', FALSE), (20, 'Fuel supply', FALSE);

-- Quiz 5: Renewable Energy
INSERT INTO questions (quiz_id, question_text) VALUES
(5, 'What do solar panels use to generate electricity?'),
(5, 'What does a wind turbine convert into electricity?'),
(5, 'What is a common feature of hydropower plants?'),
(5, 'What is biomass energy derived from?'),
(5, 'Which of these is NOT a renewable energy source?');

INSERT INTO options (question_id, option_text, is_correct) VALUES
(21, 'Photovoltaic cells', TRUE), (21, 'Combustion engines', FALSE), (21, 'Steam turbines only', FALSE), (21, 'Battery chemicals', FALSE),
(22, 'Kinetic energy of wind', TRUE), (22, 'Solar radiation', FALSE), (22, 'Chemical energy', FALSE), (22, 'Nuclear energy', FALSE),
(23, 'Dams that use flowing water', TRUE), (23, 'Wind turbines', FALSE), (23, 'Solar farms', FALSE), (23, 'Coal furnaces', FALSE),
(24, 'Organic material such as agricultural residue', TRUE), (24, 'Crude oil', FALSE), (24, 'Coal', FALSE), (24, 'Natural gas', FALSE),
(25, 'Coal', TRUE), (25, 'Solar', FALSE), (25, 'Wind', FALSE), (25, 'Hydropower', FALSE);

-- Quiz 6: Biodiversity
INSERT INTO questions (quiz_id, question_text) VALUES
(6, 'What does an ecosystem consist of?'),
(6, 'What is a leading cause of species endangerment?'),
(6, 'What do protected areas help conserve?'),
(6, 'What does reforestation help restore?'),
(6, 'What describes the flow of energy between organisms?');

INSERT INTO options (question_id, option_text, is_correct) VALUES
(26, 'Living organisms interacting with their environment', TRUE), (26, 'Only plants', FALSE), (26, 'Only animals', FALSE), (26, 'Only water bodies', FALSE),
(27, 'Habitat loss', TRUE), (27, 'Excess rainfall', FALSE), (27, 'Cool temperatures', FALSE), (27, 'Clean air', FALSE),
(28, 'Biodiversity', TRUE), (28, 'Traffic flow', FALSE), (28, 'Internet access', FALSE), (28, 'Urban housing', FALSE),
(29, 'Lost forest cover', TRUE), (29, 'Ocean levels', FALSE), (29, 'Air traffic', FALSE), (29, 'Mineral deposits', FALSE),
(30, 'Food chains and food webs', TRUE), (30, 'Traffic signals', FALSE), (30, 'Weather forecasts', FALSE), (30, 'Market prices', FALSE);

-- ---------------------------------------------------------------------
-- CHALLENGES (12 challenges across categories)
-- ---------------------------------------------------------------------
INSERT INTO challenges (title, description, category, difficulty, xp_reward, is_active, created_by) VALUES
('Carry a Reusable Water Bottle', 'Use a reusable bottle instead of buying single-use plastic bottles today.', 'Waste Management', 'Easy', 20, TRUE, 4),
('Plastic-Free Day', 'Avoid single-use plastic items for one full day.', 'Waste Management', 'Medium', 30, TRUE, 4),
('Segregate Your Waste', 'Separate dry, wet and recyclable waste at home today.', 'Waste Management', 'Easy', 20, TRUE, 4),
('E-Waste Drop-off', 'Take an old electronic item to a certified e-waste collection point.', 'Waste Management', 'Hard', 40, TRUE, 4),
('Switch Off Unused Lights', 'Turn off lights and appliances in empty rooms throughout the day.', 'Renewable Energy', 'Easy', 15, TRUE, 4),
('Use Public Transport or Carpool', 'Choose public transport, cycling or carpooling instead of a private vehicle.', 'Climate Change', 'Medium', 25, TRUE, 4),
('Care for a Plant', 'Water and take care of a plant at home or in your neighborhood.', 'Biodiversity', 'Easy', 15, TRUE, 4),
('Save Water While Brushing', 'Turn off the tap while brushing your teeth for the whole day.', 'Water Conservation', 'Easy', 15, TRUE, 4),
('Avoid Unnecessary Printing', 'Go paperless for all your tasks today.', 'Waste Management', 'Easy', 15, TRUE, 4),
('Fix a Water Leak', 'Check your home for leaking taps or pipes and report/fix one.', 'Water Conservation', 'Medium', 25, TRUE, 4),
('Start Composting', 'Set aside kitchen vegetable peels for composting instead of throwing them away.', 'Waste Management', 'Medium', 30, TRUE, 4),
('Plant a Native Sapling', 'Plant a native tree or sapling in your community.', 'Biodiversity', 'Hard', 40, TRUE, 4);

-- ---------------------------------------------------------------------
-- BADGES (6 badges)
-- ---------------------------------------------------------------------
INSERT INTO badges (name, description, icon, criteria_type, criteria_value, criteria_category) VALUES
('Green Beginner', 'Complete your first lesson.', '🌱', 'lessons_completed', 1, NULL),
('Eco Learner', 'Complete 5 quizzes.', '📘', 'quizzes_completed', 5, NULL),
('Recycling Hero', 'Complete 5 waste-management challenges.', '♻️', 'challenges_category', 5, 'Waste Management'),
('Water Guardian', 'Complete 3 water-conservation challenges.', '💧', 'challenges_category', 3, 'Water Conservation'),
('7-Day Streak', 'Maintain a 7-day activity streak.', '🔥', 'streak_days', 7, NULL),
('Eco Champion', 'Reach 1000 total XP.', '🏆', 'total_xp', 1000, NULL);

-- ---------------------------------------------------------------------
-- Demo activity for student1 (Anurag) so the dashboard has real data
-- ---------------------------------------------------------------------
INSERT INTO lesson_completions (user_id, lesson_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 5), (1, 7), (1, 9), (1, 10), (1, 11);

INSERT INTO user_progress (user_id, topic_id, lessons_completed, total_lessons, progress_percent) VALUES
(1, 1, 2, 2, 100),
(1, 2, 1, 2, 50),
(1, 3, 1, 2, 50),
(1, 4, 1, 2, 50),
(1, 5, 2, 2, 100),
(1, 6, 1, 2, 50);

INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, xp_earned, attempted_at) VALUES
(1, 1, 5, 5, 100, NOW() - INTERVAL 6 DAY),
(1, 2, 4, 5, 40, NOW() - INTERVAL 4 DAY),
(1, 5, 5, 5, 100, NOW() - INTERVAL 2 DAY);

INSERT INTO challenge_completions (user_id, challenge_id, completed_on, xp_earned) VALUES
(1, 1, CURDATE() - INTERVAL 6 DAY, 20),
(1, 5, CURDATE() - INTERVAL 5 DAY, 15),
(1, 7, CURDATE() - INTERVAL 4 DAY, 15),
(1, 8, CURDATE() - INTERVAL 3 DAY, 15),
(1, 3, CURDATE() - INTERVAL 2 DAY, 20),
(1, 9, CURDATE() - INTERVAL 1 DAY, 15),
(1, 6, CURDATE(), 25);

INSERT INTO user_badges (user_id, badge_id) VALUES
(1, 1), (1, 2), (1, 5);

INSERT INTO activity_log (user_id, activity_type, description, xp_change, activity_date) VALUES
(1, 'lesson_completed', 'Completed lesson: The Greenhouse Effect', 10, CURDATE() - INTERVAL 6 DAY),
(1, 'quiz_attempted', 'Attempted Climate Change Quiz - Score 5/5', 100, CURDATE() - INTERVAL 6 DAY),
(1, 'challenge_completed', 'Completed challenge: Carry a Reusable Water Bottle', 20, CURDATE() - INTERVAL 6 DAY),
(1, 'challenge_completed', 'Completed challenge: Switch Off Unused Lights', 15, CURDATE() - INTERVAL 5 DAY),
(1, 'quiz_attempted', 'Attempted Pollution Quiz - Score 4/5', 40, CURDATE() - INTERVAL 4 DAY),
(1, 'challenge_completed', 'Completed challenge: Care for a Plant', 15, CURDATE() - INTERVAL 4 DAY),
(1, 'challenge_completed', 'Completed challenge: Save Water While Brushing', 15, CURDATE() - INTERVAL 3 DAY),
(1, 'quiz_attempted', 'Attempted Renewable Energy Quiz - Score 5/5', 100, CURDATE() - INTERVAL 2 DAY),
(1, 'challenge_completed', 'Completed challenge: Segregate Your Waste', 20, CURDATE() - INTERVAL 2 DAY),
(1, 'challenge_completed', 'Completed challenge: Avoid Unnecessary Printing', 15, CURDATE() - INTERVAL 1 DAY),
(1, 'challenge_completed', 'Completed challenge: Use Public Transport or Carpool', 25, CURDATE());
