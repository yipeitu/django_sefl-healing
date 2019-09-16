import django.core.exceptions as dc_exceptions
from django.urls.exceptions import NoReverseMatch
from django.shortcuts import render
import os
from .urls import urlpatterns
dir_path = os.path.dirname(os.path.realpath(__file__))

class self_headling_middleware:
	def __init__(self, get_response):
		self.get_response = get_response
		self.bool_exception = False
		# One-time configuration and initialization.

	def __call__(self, request):
		# Code to be executed for each request before
		# the view (and later middleware) are called.
		print('request:', request)
		response = self.get_response(request)
		while self.bool_exception:
			self.bool_exception = False
			response = self.get_response(request)
		# after exception, it will comes to here
		print('response:', response)
		# Code to be executed for each request/response after
		# the view is called.
		return response

	def process_exception(self, request, exception):
		return render(request, 'error.html', {'error': exception})
		self.bool_exception = True
		print('process_exception request:', request.path_info)

		# error_string = exception.template_debug['during']
		error_html = exception.template_debug['name']
		error_string_start = exception.template_debug['start']
		error_string_end = exception.template_debug['end']
		url_list = urlpatterns

		path = request.path_info.split("/")[-1]
		resolver_match = None
		for url in url_list:
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
				# 3) Arguments or Keyword arguments
				if "with no arguments not found" in exception.args[0]:
					# parameter type
					if 'int' in resolver_match.route:
						path = "3"

				# 1) Using wrong URL name in template html file.
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
		else:
			# default error handler
			return render(request, 'error.html', {'error': exception})

