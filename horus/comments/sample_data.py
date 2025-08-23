"""
Horus Comments Sample Data
=========================

Sample VFX review comments for demonstration purposes.
"""


def create_sample_vfx_comments():
    """Create sample VFX review comments with realistic content."""
    return [
        {
            "id": 1,
            "user": "John Doe",
            "avatar": "JD",
            "time": "2 hours ago",
            "frame": None,
            "text": "The lighting in this shot looks great! Ready for comp.",
            "likes": 5,
            "replies": [
                {
                    "id": 2,
                    "user": "Jane Smith",
                    "avatar": "JS",
                    "time": "1 hour ago",
                    "text": "@john.doe Agreed! Color temp is perfect.",
                    "likes": 2
                },
                {
                    "id": 3,
                    "user": "Mike Wilson",
                    "avatar": "MW",
                    "time": "30 min ago",
                    "text": "Can we get a version without the rim light?",
                    "likes": 1
                }
            ]
        },
        {
            "id": 4,
            "user": "Sarah Chen",
            "avatar": "SC",
            "time": "3 hours ago",
            "frame": 1047,
            "text": "The eye line doesn't match the previous shot",
            "likes": 3,
            "status": "Open",
            "priority": "High",
            "replies": [
                {
                    "id": 5,
                    "user": "Director",
                    "avatar": "DR",
                    "time": "2 hours ago",
                    "text": "Good catch! Please adjust in the next version.",
                    "likes": 1
                }
            ]
        },
        {
            "id": 6,
            "user": "Alex Rodriguez",
            "avatar": "AR",
            "time": "4 hours ago",
            "frame": 1052,
            "text": "Shadows are too dark in this area",
            "likes": 1,
            "status": "Resolved",
            "priority": "Medium",
            "replies": []
        },
        {
            "id": 7,
            "user": "Emily Davis",
            "avatar": "ED",
            "time": "5 hours ago",
            "frame": None,
            "text": "Overall sequence timing feels good. Nice work team! 🔥",
            "likes": 8,
            "replies": [
                {
                    "id": 8,
                    "user": "Tom Brown",
                    "avatar": "TB",
                    "time": "4 hours ago",
                    "text": "Thanks! The new edit really helps the pacing.",
                    "likes": 3
                },
                {
                    "id": 9,
                    "user": "Lisa Wang",
                    "avatar": "LW",
                    "time": "3 hours ago",
                    "text": "Agreed, much better flow now.",
                    "likes": 2
                }
            ]
        },
        {
            "id": 10,
            "user": "Chris Johnson",
            "avatar": "CJ",
            "time": "6 hours ago",
            "frame": 1089,
            "text": "Particle simulation needs more density in the background",
            "likes": 2,
            "status": "In Progress",
            "priority": "Medium",
            "replies": [
                {
                    "id": 11,
                    "user": "FX Artist",
                    "avatar": "FX",
                    "time": "5 hours ago",
                    "text": "Working on it! Should have an update by EOD.",
                    "likes": 1
                }
            ]
        }
    ]
