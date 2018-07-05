import re, math, os
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot, row, layout
from bokeh.models import ColumnDataSource, ranges, LabelSet, Div, SingleIntervalTicker, LinearAxis

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import numpy as np
from bs4 import BeautifulSoup


class Chat(object):
	def __init__(self, file):
		"""Initialises the object with file-name and fetches the content into self.chat_cntnt"""
		self.file = file
		with open(self.file, "r") as chat:
			self.chat_cntnt = chat.read()

	# Analysis point 1, 4.
	def number_of_messages(self):
		"""Finds and returns self.tot_num_msgs and self.num_media"""
		pttrn_num_msgs = re.compile(r'\b\d*/\d*/\d*, \d*:\d* [AP]M - (.*?): ')
		matches = pttrn_num_msgs.findall(self.chat_cntnt)
		self.tot_num_msgs = len(matches)
		pttrn_num_media = re.compile(r'\s<Media omitted>')
		matches = pttrn_num_media.findall(self.chat_cntnt)
		self.num_media = len(matches)
		return self.tot_num_msgs, self.num_media

	# Analysis point 2 and member list.
	def number_of_contributing_members(self):
		"""Finds and returns self.num_mem and self.member_list"""
		members = re.findall(r'\b\d*/\d*/\d*, \d*:\d* [AP]M - (.*?): ', self.chat_cntnt)
		self.member_list = list(set(members))
		self.member_list_set = set(members)
		self.num_mem = len(self.member_list)
		for idx, peep in enumerate(self.member_list):
			if u'\u202a' in peep:
				self.member_list[idx] = peep.strip(u'\u202a')
			if u'\u202c' in peep:
				self.member_list[idx] = self.member_list[idx].strip(u'\u202c')
		return self.num_mem, self.member_list

	# Analysis point 3, 3a and 3b. 
	# (dependent on self.number_of_contributing_members())
	def message_by_member_splitup(self):
		# self.number_of_contributing_members()
		self.mem_msg_splitup = {}
		for peep in self.member_list_set:
			pttrn_mem_by_msg = re.compile(r'\b\d*/\d*/\d*, \d*:\d* [AP]M - '+re.escape(peep)+r': ')
			matches = pttrn_mem_by_msg.findall(self.chat_cntnt)
			self.mem_msg_splitup[peep.strip(u'\u202a').strip(u'\u202c')] = len(matches)
		self.max_msg_peep = max(self.mem_msg_splitup, key=self.mem_msg_splitup.get)
		self.numMsgs_by_max_msg_peep = max(self.mem_msg_splitup.values())
		self.min_msg_peep =	min(self.mem_msg_splitup, key=self.mem_msg_splitup.get)
		self.numMsgs_by_min_msg_peep = min(self.mem_msg_splitup.values())
		return self.mem_msg_splitup, {self.max_msg_peep:self.numMsgs_by_max_msg_peep}, {self.min_msg_peep:self.numMsgs_by_min_msg_peep}

	# Analysis point 5 and 5a.
	# (dependent on self.number_of_contributing_members())
	def media_by_member_splitup(self):
		# self.number_of_contributing_members()
		self.mem_media_splitup = {}
		for peep in self.member_list_set:
			pttrn_media_by_mem = re.compile(r'\b\d*/\d*/\d*, \d*:\d* [AP]M - '+re.escape(peep)+r':\s<Media omitted>')
			matches = pttrn_media_by_mem.findall(self.chat_cntnt)
			self.mem_media_splitup[peep.strip(u'\u202a').strip(u'\u202c')] = len(matches)
		self.max_media_peep = max(self.mem_media_splitup, key=self.mem_media_splitup.get)
		self.numMedia_by_max_media_peep = max(self.mem_media_splitup.values())
		self.min_media_peep = min(self.mem_media_splitup, key=self.mem_media_splitup.get)
		self.numMedia_by_min_media_peep = min(self.mem_media_splitup.values())
		return self.mem_media_splitup, {self.max_media_peep:self.numMedia_by_max_media_peep}, {self.min_media_peep:self.numMedia_by_min_media_peep}

	def time_stats(self):
		'''Returns (time-span of chat, time of first message, time of second message, msg timestamp list, msg datestamp list, msg hourstamp list, msg monthstamp list)'''
		self.msg_timestamps = []
		self.msg_datestamps = []
		self.msg_hourstamps = []
		self.msg_monthstamps = []

		self.media_timestamps = []
		self.media_datestamps = []
		self.media_hourstamps = []
		self.media_monthstamps = []

		for msg_ln in self.chat_cntnt.splitlines():
			pttrn_new_datetime = re.compile(r'(\b\d*/\d*/\d*, \d*:\d* [AP]M) - .*?:')
			pttrn_new_date = re.compile(r'(\b\d*/\d*/\d*), \d*:\d* [AP]M - .*?:')
			pttrn_new_hour = re.compile(r'(\b\d*/\d*/\d*), (\d*):\d* ([AP]M) - .*?:')
			pttrn_new_month = re.compile(r'\b\d*/(\d*/\d*), \d*:\d* [AP]M - .*?:')

			pttrn_new_datetime_media = re.compile(r'(\b\d*/\d*/\d*, \d*:\d* [AP]M) - .*?: <Media omitted>')
			pttrn_new_date_media = re.compile(r'(\b\d*/\d*/\d*), \d*:\d* [AP]M - .*?: <Media omitted>')
			pttrn_new_hour_media = re.compile(r'(\b\d*/\d*/\d*), (\d*):\d* ([AP]M) - .*?: <Media omitted>')
			pttrn_new_month_media = re.compile(r'\b\d*/(\d*/\d*), \d*:\d* [AP]M - .*?: <Media omitted>')

			datetime_matches = pttrn_new_datetime.findall(msg_ln)
			date_matches = pttrn_new_date.findall(msg_ln)
			hour_matches = pttrn_new_hour.findall(msg_ln)
			month_matches = pttrn_new_month.findall(msg_ln)

			datetime_matches_media = pttrn_new_datetime_media.findall(msg_ln)
			date_matches_media = pttrn_new_date_media.findall(msg_ln)
			hour_matches_media = pttrn_new_hour_media.findall(msg_ln)
			month_matches_media = pttrn_new_month_media.findall(msg_ln)

			if len(datetime_matches) == 1:
				self.msg_timestamps.append(datetime_matches[0])
				self.msg_datestamps.append(date_matches[0])
				self.msg_hourstamps.append(' '.join(hour_matches[0]))
				self.msg_monthstamps.append(month_matches[0])

			if len(datetime_matches_media) == 1:
				self.media_timestamps.append(datetime_matches_media[0])
				self.media_datestamps.append(date_matches_media[0])
				self.media_hourstamps.append(' '.join(hour_matches_media[0]))
				self.media_monthstamps.append(month_matches_media[0])

		self.chat_timeLength = datetime.strptime(self.msg_timestamps[-1], '%d/%m/%y, %I:%M %p') - datetime.strptime(self.msg_timestamps[0], '%d/%m/%y, %I:%M %p')
		return (self.chat_timeLength, 
				self.msg_timestamps[0], self.msg_timestamps[-1], self.msg_timestamps, 
				self.msg_datestamps, 
				self.msg_hourstamps, 
				self.msg_monthstamps,
				self.media_timestamps,
				self.media_datestamps,
				self.media_hourstamps,
				self.media_monthstamps
				)



	def dash_it_up(self):
		# print("DASH IT UP BEGIN:\t\t" + datetime.strftime(datetime.now(), '%I:%M:%S'))
		total_num_messages, total_num_media = self.number_of_messages()
		# print("self.number_of_messages() executed")
		num_members, member_list = self.number_of_contributing_members()
		# print("self.number_of_contributing_members() executed")
		member_numMsg_dict, max_msg_peep_dict, min_msg_peep_dict = self.message_by_member_splitup()
		# print("self.message_by_member_splitup() executed")
		member_numMedia_dict, max_media_peep_dict, min_media_peep_dict = self.media_by_member_splitup()
		# print("self.media_by_member_splitup() executed")
		chat_timespan, msg_one_t, msg_last_t, all_times, all_dates, all_hours, all_months, all_times_media, all_dates_media, all_hours_media, all_months_media= self.time_stats()
		# print("self.time_stats() executed")

		output_file("./HTMLs/_STATISTICS_{}.html".format(os.path.basename(os.path.splitext(self.file)[0])))

		# page_font = "SF Pro Display"	
		
		#PLOT 0: TITLE OF THE PAGE===========================================================================================================================#
		title_plot = figure(plot_height=30, logo=None)
		title_plot.title.text = "{} ({} participants)".format(os.path.basename(os.path.splitext(self.file)[0]), num_members)
		# title_plot.title.text_font = "SF Pro Display"
		title_plot.title.text_font_size = "55px"
		title_plot.title.text_font_style = "bold"
		title_plot.title.align = "center"

		#DISTRIBUTION PLOT SETTINGS====================================================#
		title_text_font_size = "40px"
		xtick_font_size_value = (-1/7*num_members + 152/7) if num_members>=20 else 16
		xtick_text_font_size = "{}px".format(xtick_font_size_value)
		individual_bar_label_size = "{}px".format(xtick_font_size_value)

		colors = [""]
		#PLOT 1: MESSAGE DISTRIBUTION===========================================================================================================================#
		source = ColumnDataSource(dict(x=list(self.mem_msg_splitup.keys()), y=list(self.mem_msg_splitup.values())))

		plot1 = figure(x_range=list(self.mem_msg_splitup.keys()), logo=None, sizing_mode="scale_width", plot_height=400)
		plot1.title.text = "Messages: {}".format(total_num_messages)
		plot1.title.text_font_size = title_text_font_size
		# plot1.title.text_font = page_font
		labels = LabelSet(x='x', y='y', text='y', level='glyph',
							x_offset=-xtick_font_size_value/2, y_offset=0, source=source, render_mode='canvas', 
							text_font_size=individual_bar_label_size, 
							# text_font=page_font
							)
		plot1.vbar(	source=source,
					x='x',
					top='y',
					width=0.8)
		plot1.add_layout(labels)
		plot1.xgrid.grid_line_color = None
		plot1.y_range.start = 0

		plot1.xaxis.major_label_orientation = math.pi/2
		plot1.xaxis.major_label_text_font_size = xtick_text_font_size
		# plot1.xaxis.major_label_text_font = page_font

		plot1.yaxis.axis_label = "#messages"
		plot1.yaxis.major_label_orientation = math.pi/2
		# plot1.yaxis.major_label_text_font = page_font
		plot1.yaxis.major_label_text_font_size = "16px"
		plot1.yaxis.axis_label_text_font_size = "16px"
		# plot1.yaxis.axis_label_text_font = page_font


		#PLOT 2: MEDIA DISTRIBUTION===========================================================================================================================#
		source = ColumnDataSource(dict(x=list(self.mem_media_splitup.keys()), y=list(self.mem_media_splitup.values())))
		plot2 = figure(x_range=list(self.mem_media_splitup.keys()), logo=None, sizing_mode="scale_width", plot_height=400)
		plot2.title.text = "Media: {}".format(total_num_media)
		plot2.title.text_font_size = title_text_font_size
		# plot2.title.text_font = page_font
		labels = LabelSet(x='x', y='y', text='y', level='glyph',
							x_offset=-xtick_font_size_value/2, y_offset=0, source=source, render_mode='canvas', 
							text_font_size=individual_bar_label_size, 
							# text_font=page_font
							)
		plot2.vbar(	source=source,
					x='x',
					top='y',
					width=0.8, color="firebrick")
		plot2.add_layout(labels)
		plot2.xgrid.grid_line_color = None
		plot2.y_range.start = 0

		plot2.xaxis.major_label_orientation = math.pi/2
		plot2.xaxis.major_label_text_font_size = xtick_text_font_size
		# plot2.xaxis.major_label_text_font = page_font

		plot2.yaxis.axis_label = "#media"
		plot2.yaxis.major_label_orientation = math.pi/2
		# plot2.yaxis.major_label_text_font = page_font
		# plot2.yaxis.major_label_text_font_size = "16px"
		plot2.yaxis.axis_label_text_font_size = "16px"
		# plot2.yaxis.axis_label_text_font = page_font

		#PLOT 3: MEMBER LIST & (TOTAL NUMBER OF MEMBERS)===========================================================================================================================#
		plot3 = figure(plot_height=13, logo=None, sizing_mode="scale_width")
		name_str = ''
		for x in member_list:
			if name_str == '':
				name_str += x
			else:
				name_str += ', '+x
		plot3.title.text = "Participants ({}): {}".format(num_members, name_str)
		plot3.title.text_font_size = "18px"
		# plot3.title.text_font = page_font
		plot3.title.text_font_style = "normal"
		plot3.title.align = "center"

		#TIME DISTRIBUTION PLOTS' LOCAL FUNCTIONS===========================================================#
		def perdelta(start, end, delta):
			curr = start
			while curr<end:
				yield curr
				curr += delta

		def timeBlockSpan(first, last):
			"""
			Returns:	1 ==> minutes 	(very new chat)
						2 ==> hours		(relatively new chat)
						3 ==> days		(relatively old chat)
						4 ==> months	(established chat)(cancelled)
			"""
			t_delta = last - first
			if t_delta.total_seconds() <= 3600:
				return 1
			elif 3600 < t_delta.total_seconds() <= 259200:
				return 2
			elif 259200 < t_delta.total_seconds() and t_delta.days <= 91:
				return 3
			elif t_delta.days > 91:
				return 4

		#PLOT 4: MESSAGE TIME DISTRIBUTION===========================================================================================================================#
		
		# print("Begin" + datetime.strftime(datetime.now(), '%I:%M:%S'))

		all_dates_dtObjs = []
		for stamp in all_dates:
			all_dates_dtObjs.append(datetime.strptime(stamp, '%d/%m/%y').date())

		all_times_dtObjs = []
		for stamp in all_times:
			all_times_dtObjs.append(datetime.strptime(stamp, '%d/%m/%y, %I:%M %p'))

		all_hours_dtObjs = []
		for stamp in all_hours:
			all_hours_dtObjs.append(datetime.strptime(stamp, '%d/%m/%y %I %p'))

		all_months_dtObjs = []
		for stamp in all_months:
			all_months_dtObjs.append(datetime.strptime(stamp, '%m/%y'))

		# print("created all dtObjs" + datetime.strftime(datetime.now(), '%I:%M:%S'))

		first_date, last_date = all_dates_dtObjs[0], all_dates_dtObjs[-1]
		first_dt, last_dt = all_times_dtObjs[0], all_times_dtObjs[-1]
		first_hour, last_hour = all_hours_dtObjs[0], all_hours_dtObjs[-1]
		first_month, last_month = all_months_dtObjs[0], all_months_dtObjs[-1]

		timeBlockSpan_decision = timeBlockSpan(first_dt, last_dt)



		# print("TBS decision generated" + datetime.strftime(datetime.now(), '%I:%M:%S'))

		if timeBlockSpan_decision == 1:
			all_times_msgs_distr = {}
			for i in perdelta(first_dt, last_dt+timedelta(seconds=60), timedelta(seconds=60)):
				all_times_msgs_distr[i] = all_times_dtObjs.count(i)

			xLabels = [datetime.strftime(x, "%I:%M %p") for x in all_times_msgs_distr.keys()]
			y = list(all_times_msgs_distr.values())

		elif timeBlockSpan_decision == 2:
			all_hours_msgs_distr = {}
			for i in perdelta(first_hour, last_hour+timedelta(hours=1), timedelta(hours=1)):
				all_hours_msgs_distr[i] = all_hours_dtObjs.count(i)

			xLabels = [datetime.strftime(x, "%d/%m, %H-{} hours".format(x.hour+1)) for x in all_hours_msgs_distr.keys()]
			y = list(all_hours_msgs_distr.values())

		elif timeBlockSpan_decision == 3:
			all_dates_msgs_distr = {}
			for i in perdelta(first_date, last_date+timedelta(days=1), timedelta(days=1)):
				all_dates_msgs_distr[i] = all_dates_dtObjs.count(i)

			xLabels = [datetime.strftime(x, "%d %B '%y") for x in all_dates_msgs_distr.keys()]
			y = list(all_dates_msgs_distr.values())

		elif timeBlockSpan_decision == 4:
			all_months_msgs_distr = {}
			for i in perdelta(first_month, last_month+relativedelta(months=+1), relativedelta(months=+1)):
				all_months_msgs_distr[i] = all_months_dtObjs.count(i)

			xLabels = [datetime.strftime(x, "%B '%y") for x in all_months_msgs_distr.keys()]
			y = list(all_months_msgs_distr.values())


		# print(datetime.strftime(datetime.now(), '%I:%M:%S'))

		num_bars_on_plot = len(xLabels)
		xtick_font_size_value = (-1/7*num_bars_on_plot + 152/5.5) if num_bars_on_plot>=40 else 16
		xtick_text_font_size = "{}px".format(xtick_font_size_value)
		source = ColumnDataSource(dict(x=xLabels, y=y))

		plot4 = figure(plot_height=180, logo=None, sizing_mode="scale_width", x_range=xLabels)
		plot4.title.text = "Messages time distribution [{} - {} (~{} days)]".format(msg_one_t, msg_last_t, chat_timespan.days+1)
		plot4.title.text_font_size = title_text_font_size
		labels = LabelSet(x='x', y='y', text='y', level='glyph',
							x_offset=-6, y_offset=0, source=source, render_mode='canvas', 
							text_font_size=xtick_text_font_size,
							# text_font=page_font
							)
		plot4.vbar(source=source, x='x', top='y', width=0.9, color="#9EA09E")
		plot4.add_layout(labels)
		plot4.xaxis.major_label_orientation = math.pi/2
		plot4.xaxis.major_label_text_font_size = xtick_text_font_size
		plot4.yaxis.axis_label = "Activity (#messages)"
		plot4.yaxis.axis_label_text_font_size = "16px"
		
		#PLOT 5: MEDIA TIME DISTRIBUTION===========================================================================================================================#
		all_dates_media_dtObjs = []
		for stamp in all_dates_media:
			all_dates_media_dtObjs.append(datetime.strptime(stamp, '%d/%m/%y').date())

		all_times_media_dtObjs = []
		for stamp in all_times_media:
			all_times_media_dtObjs.append(datetime.strptime(stamp, '%d/%m/%y, %I:%M %p'))

		all_hours_media_dtObjs = []
		for stamp in all_hours_media:
			all_hours_media_dtObjs.append(datetime.strptime(stamp, '%d/%m/%y %I %p'))

		all_months_media_dtObjs = []
		for stamp in all_months_media:
			all_months_media_dtObjs.append(datetime.strptime(stamp, '%m/%y'))

		# print("created all dtObjs" + datetime.strftime(datetime.now(), '%I:%M:%S'))

		first_date_media, last_date_media = all_dates_media_dtObjs[0], all_dates_media_dtObjs[-1]
		first_dt_media, last_dt_media = all_times_media_dtObjs[0], all_times_media_dtObjs[-1]
		first_hour_media, last_hour_media = all_hours_media_dtObjs[0], all_hours_media_dtObjs[-1]
		first_month_media, last_month_media = all_months_media_dtObjs[0], all_months_media_dtObjs[-1]

		timeBlockSpan_decision = timeBlockSpan(first_dt_media, last_dt_media)



		# print("TBS decision generated" + datetime.strftime(datetime.now(), '%I:%M:%S'))

		if timeBlockSpan_decision == 1:
			all_times_media_distr = {}
			for i in perdelta(first_dt_media, last_dt_media+timedelta(seconds=60), timedelta(seconds=60)):
				all_times_media_distr[i] = all_times_media_dtObjs.count(i)

			xLabels = [datetime.strftime(x, "%I:%M %p") for x in all_times_media_distr.keys()]
			y = list(all_times_media_distr.values())

		elif timeBlockSpan_decision == 2:
			all_hours_media_distr = {}
			for i in perdelta(first_hour_media, last_hour_media+timedelta(hours=1), timedelta(hours=1)):
				all_hours_media_distr[i] = all_hours_media_dtObjs.count(i)

			xLabels = [datetime.strftime(x, "%d/%m, %H-{} hours".format(x.hour+1)) for x in all_hours_media_distr.keys()]
			y = list(all_hours_media_distr.values())

		elif timeBlockSpan_decision == 3:
			all_dates_media_distr = {}
			for i in perdelta(first_date_media, last_date_media+timedelta(days=1), timedelta(days=1)):
				all_dates_media_distr[i] = all_dates_media_dtObjs.count(i)

			xLabels = [datetime.strftime(x, "%d %B '%y") for x in all_dates_media_distr.keys()]
			y = list(all_dates_media_distr.values())

		elif timeBlockSpan_decision == 4:
			all_months_media_distr = {}
			for i in perdelta(first_month_media, last_month_media+relativedelta(months=+1), relativedelta(months=+1)):
				all_months_media_distr[i] = all_months_media_dtObjs.count(i)

			xLabels = [datetime.strftime(x, "%B '%y") for x in all_months_media_distr.keys()]
			y = list(all_months_media_distr.values())


		# print(datetime.strftime(datetime.now(), '%I:%M:%S'))

		num_bars_on_plot = len(xLabels)
		xtick_font_size_value = (-1/7*num_bars_on_plot + 152/5.5) if num_bars_on_plot>=40 else 16
		xtick_text_font_size = "{}px".format(xtick_font_size_value)
		source = ColumnDataSource(dict(x=xLabels, y=y))

		plot5 = figure(plot_height=180, logo=None, sizing_mode="scale_width", x_range=xLabels)
		plot5.title.text = "Media time distribution [{} - {} (~{} days)]".format(msg_one_t, msg_last_t, chat_timespan.days+1)
		plot5.title.text_font_size = title_text_font_size
		labels = LabelSet(x='x', y='y', text='y', level='glyph',
							x_offset=-6, y_offset=0, source=source, render_mode='canvas', 
							text_font_size=xtick_text_font_size,
							# text_font=page_font
							)
		plot5.vbar(source=source, x='x', top='y', width=0.9, color="#FFC300")
		plot5.add_layout(labels)
		plot5.xaxis.major_label_orientation = math.pi/2
		plot5.xaxis.major_label_text_font_size = xtick_text_font_size
		plot5.yaxis.axis_label = "Activity (#media)"
		plot5.yaxis.axis_label_text_font_size = "16px"

		#DASHBOARD ASSIMILATION===========================================================================================================================#
		dashboard = layout(
						children=[
							[title_plot],
							[plot3],
							[plot1, plot2],
							[plot4],
							[plot5]
							], 
							sizing_mode="scale_width"
							)
		#edit html-title

		show(dashboard)
		# print("DASH IT UP END:\t\t" + datetime.strftime(datetime.now(), '%I:%M:%S'))
def main():
	chat = Chat("./chats/Whatsapp Chat with xyz.txt".format(C))
	chat.dash_it_up()
	# print("{} done at {}".format(C, datetime.strftime(datetime.now(), '%I:%M:%S %p')))
	
if __name__ == '__main__':
	main()