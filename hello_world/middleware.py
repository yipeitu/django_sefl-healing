import django.core.exceptions as dc_exceptions
from django.urls import path, include
from django.urls.exceptions import NoReverseMatch
from django.shortcuts import render
from django.db import OperationalError, ProgrammingError, DatabaseError, IntegrityError
from .settings import *
import os
from .urls import urlpatterns
dir_path = os.path.dirname(os.path.realpath(__file__))


class self_healing_middleware:
	def __init__(self, get_response):
		self.get_response = get_response
		self.bool_exception = False
		# One-time configuration and initialization.

	def __call__(self, request):
		# Code to be executed for each request before
		# the view (and later middleware) are called.
		print('request:', request)
		response = self.get_response(request)

		####################################################
		# 4) Including app URL conf in project urls.py
		####################################################
		# if response.status_code == 404:
		# 	self.bool_exception = True
		# 	for app in INSTALLED_APPS:
		# 		bool_add = False
		# 		if "django.contrib." in app:
		# 			continue
		# 		for url_path in urlpatterns:
		# 			print(url_path)
		# 			if url_path.app_name == app or url_path.namespace == app:
		# 				break
		# 			else:
		# 				bool_add = True
		# 		if bool_add:
		# 			self.bool_exception = True
		# 			# urlpatterns.append(path(app+'/', include((app+'.urls', app))))
		# 			urlpatterns.append(path(app + '/', include(app + '.urls')))
		####################################################
		# multiple errors
		####################################################
		for i in range(3):
			if self.bool_exception:
				self.bool_exception = False
				response = self.get_response(request)
			else:
				break
		####################################################
		# can't solve errors
		####################################################
		# if self.bool_exception:
		# 	response = render(request, 'error.html', {'error': "INTERNAL ERROR"})
		# after exception, it will comes to here
		print('response:', response)
		# Code to be executed for each request/response after
		# the view is called.
		return response

	def process_exception(self, request, exception):
		self.bool_exception = True
		print('process_exception request:', request.path_info)

		# error_string = exception.template_debug['during']
		error_html = exception.template_debug['name']
		error_string_start = exception.template_debug['start']
		error_string_end = exception.template_debug['end']

		path = request.path_info.split("/")[-1]
		resolver_match = None
		url_list = []
		print(url_list)
		for url_class in urlpatterns:
			url_list += url_class.url_patterns
		for url in url_list:
			# CHECK HOW TO MATCH
			resolver_match = url.resolve(path)
			if resolver_match is not None:
				break
		print(exception)
		if type(exception) == NoReverseMatch:
			origin_html = ""
			with open(exception.template_debug['name']) as f:
				origin_html = f.read()
			if len(origin_html) > error_string_end:
				error_string = origin_html[error_string_start:error_string_end]
				print(error_string)
				url_name = resolver_match.url_name
				new_html = origin_html
				####################################################
				# 3) Arguments or Keyword arguments
				####################################################
				if "with no arguments not found" in exception.args[0]:
					# parameter type
					if 'int' in resolver_match.route:
						path = "3"
				####################################################
				# 1) Using wrong URL name in template html file.
				####################################################
				elif "not found" in exception.args[0]:
					pass

				repair_string = "{% url '"+url_name+"' "+path+" %}"

				new_html = "".join((origin_html[:error_string_start], repair_string, origin_html[error_string_end:]))
				# rename file

				os.rename(exception.template_debug['name'], exception.template_debug['name']+".bk")
				# html_repair_name = exception.template_debug['name'].replace(".html", "_repair.html")
				html_repair_name = exception.template_debug['name']
				with open(html_repair_name, "w") as fw:
					fw.write(new_html)
		# 		return
		elif type(exception) in [OperationalError, ProgrammingError, DatabaseError, IntegrityError]:
			# fix database error, restart/migrate database, return error.html
			self.bool_exception = False
			return render(request, 'error.html', {'error': exception})
		# else:
		# 	# default error page
		# 	self.bool_exception = False
		# 	return render(request, 'error.html', {'error': exception})

