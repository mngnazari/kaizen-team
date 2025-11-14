# utils/constants.py

"""
تمام States و Constants مورد استفاده در پروژه
"""

# ==================== Registration States ====================
GET_FULL_NAME, GET_PHONE = range(2)

# ==================== Employee Task States ====================
(
    TASK_START_CONFIRMATION,
    TASK_WORK_VIEW
) = range(10, 12)

# ==================== Category States ====================
GET_CATEGORY_NAME = 30

# ==================== User Management States ====================
AWAITING_CONFIRMATION = 40

# ==================== Work States (Employee) - Old ====================
(
    WORK_KNOWLEDGE_TEXT, WORK_KNOWLEDGE_FILE,
    WORK_SUGGESTION_TEXT, WORK_SUGGESTION_FILE,
    WORK_RESULTS_TEXT, WORK_RESULTS_FILE,
    WORK_SELF_SCORE
) = range(40, 47)

# ==================== Work States (Employee) - New (Unified) ====================
(
    WORK_KNOWLEDGE_ENTRY,
    WORK_SUGGESTION_ENTRY,
    WORK_RESULTS_ENTRY,
    WORK_SELF_SCORE_ENTRY
) = range(100, 104)

# ==================== Admin Review States ====================
(
    ADMIN_REVIEW_OPINION_TEXT, ADMIN_REVIEW_OPINION_FILE,
    ADMIN_REVIEW_POSITIVE_TEXT, ADMIN_REVIEW_POSITIVE_FILE,
    ADMIN_REVIEW_NEGATIVE_TEXT, ADMIN_REVIEW_NEGATIVE_FILE,
    ADMIN_REVIEW_SUGGESTION_TEXT, ADMIN_REVIEW_SUGGESTION_FILE,
    ADMIN_TASK_SCORE
) = range(50, 59)

# ==================== Task Status Constants ====================
TASK_STATUS_PENDING = 'pending'
TASK_STATUS_IN_PROGRESS = 'in_progress'
TASK_STATUS_COMPLETED = 'completed'
TASK_STATUS_ON_HOLD = 'on_hold'
TASK_STATUS_ARCHIVED = 'archived'

# ==================== User Role Constants ====================
ROLE_ADMIN = 'admin'
ROLE_EMPLOYEE = 'employee'
ROLE_PENDING = 'pending'

# ==================== Work Data Types ====================
DATA_TYPE_KNOWLEDGE = 'knowledge'
DATA_TYPE_SUGGESTION = 'suggestion'
DATA_TYPE_RESULTS = 'results'

# ==================== Review Types ====================
REVIEW_TYPE_OPINION = 'opinion'
REVIEW_TYPE_POSITIVE = 'positive'
REVIEW_TYPE_NEGATIVE = 'negative'
REVIEW_TYPE_SUGGESTION = 'suggestion'
REVIEW_TYPE_SCORE = 'score'

# ==================== File Types ====================
FILE_TYPE_PHOTO = 'photo'
FILE_TYPE_VIDEO = 'video'
FILE_TYPE_VOICE = 'voice'
FILE_TYPE_DOCUMENT = 'document'

# ==================== Section Types ====================
SECTION_TYPE_RESULTS = 'results'
SECTION_TYPE_DESCRIPTION = 'description'