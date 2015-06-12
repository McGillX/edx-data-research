"""
In this module we define the interface between the cli input provided
by the user and the analytics required by the user
"""
from edx_data_research.reporting import basic
from edx_data_research.reporting.edx_base import EdX

def cmd_list_basic(args):
	"""
	List the basic analytics commands and their summary
	"""
	pass
	
def cmd_list_all(args):
	"""
	List all the analytics commands and their summary
	"""
	pass
	
def cmd_run_basic(args):
	"""
	Run basic analytics
	"""
	pass

def cmd_run_ip_to_country(args):
    """
    Map IP to Country for each student (if applicable)
    """
    edx_obj = EdX(args)
    basic.ip_to_country(edx_obj)

def cmd_run_user_info(args):
    """
    Retrieve information about students registered in the course
    """
    edx_obj = EdX(args)
    basic.user_info(edx_obj)

def cmd_run_course_completers(args):
    """
    Retrieve users who have completed a course 
    """
    edx_obj = EdX(args)
    basic.course_completers(edx_obj)
