from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from django import newforms as forms
from django.newforms.util import ErrorList

from roadmate.models.location import Location
from roadmate.models.roadmateuser import RoadMateUser

from roadmate.widgets.selectdatewidget import SelectDateWidget
from roadmate.widgets.selecttimewidget import SelectTimeWidget

class Ride(db.Model):
	"""
		An instance of a ride.

		For Prototype 3 The Ride will be given
		the ability to recur by creating itself at intervals.
		Thus recurring rides (commutes) can be established.
		 _______
		| RIDE |--|
		|------|  | <<creates>>
		|      |<-|
		|______|

		Use Ride.seats to get the collection of child Seats
	"""


	owner = db.ReferenceProperty(RoadMateUser, collection_name="rides", required=True)
	source = db.ReferenceProperty(Location, verbose_name="From", collection_name="rides_from", required=True) ##where the ride begins
	destination = db.ReferenceProperty(Location, verbose_name="To", collection_name="rides_to", required=True) ##where it will end
	date = db.DateProperty(verbose_name="Date") ##date of this ride
	departure_time = db.TimeProperty(verbose_name="Departure time") ##time of this ride departure
	arrival_time = db.TimeProperty(verbose_name="Arrival time") ##date of this ride
	notes = db.TextProperty(verbose_name="Notes")##any comments the owner wants to make about this ride
	created = db.DateTimeProperty(required=True, auto_now_add=True) ##date this ride was created

	# return the number of seats
	def count_seats(self):
		return self.seats.count()

	# return the number of unassigned seats
	def count_emptyseats(self):
		return self.seats.filter('passenger = ', None).count()

	# return the number of assigned seats
	def count_passengers(self):
		return self.count_seats() - self.count_emptyseats()

	# return TRUE if user is a passenger on this ride
	def is_passenger(self,user):
		return (self.seats.filter('passenger = ', user).count() > 0)

	# return a formatted textual description of the ride's status
	# we could make this conditional to show some alt text (in red?) if the ride is full
	# this saves having 2 columns "Seats" and "Passengers" - wasting half the table width on the browse pages
	def status(self):
		return self.count_seats().__str__() + " seats<br/>" + self.count_passengers().__str__() + " passengers"

	# create_seats
	# method to create a number_of_seats
	# can only be invoked after the Ride has been saved
	def create_seats(self, number_of_seats):
		from roadmate.models.seat import Seat
		for i in range(0,number_of_seats):
			s = Seat(ride=self)
			s.put()
		return

	# get_name
	# use this method to define a standard
	# fornat of displaying the reference to a ride
	def get_name(self):
		return self.source.get_addressname() + " to " + self.destination.get_addressname()

 	def __unicode__(self):
		"""Returns a string representation of the object."""
		return self.get_name()


class RideForm(djangoforms.ModelForm):
	"""
		Form to create a Ride

		This form has come from what was RideOfferForm in the RideOffer model.
		For Prototype 3, RideOffer is now deprecated and Ride creation is handled by the Ride entity

	"""

	# ------------------------------------------------------------------------
	#  Set the widgets we want for these attributes of Ride
	# ------------------------------------------------------------------------
	date = forms.DateField(widget=SelectDateWidget) #TODO set defaults/initialization on these, they are null otherwise
	departure_time = forms.TimeField(widget=SelectTimeWidget)
	arrival_time = forms.TimeField(widget=SelectTimeWidget)
	number_of_seats = forms.IntegerField(initial=1)
	source = djangoforms.ModelChoiceField(Location, label="From location", required=False)
	destination = djangoforms.ModelChoiceField(Location, label="To location", required=False)

	# ------------------------------------------------------------------------
	#  Alternative text fields for source and destination
	# ------------------------------------------------------------------------
	source_address = forms.CharField(label="From address", required=False)
	destination_address = forms.CharField(label="To address", required=False)


	def clean_number_of_seats(self):
		number_of_seats = self.clean_data['number_of_seats']

		#TODO: this shouldn't be hardcoded
		if number_of_seats < 1:
			raise forms.ValidationError("Number of seats must be atleast one.")
		if number_of_seats > 80:
			raise forms.ValidationError("Number of seats cannot be more than 80.")

		return number_of_seats

	def clean(self):
		cleaned_data = self.clean_data

		owner = cleaned_data['owner'] = self.initial['owner']
		errors = ErrorList()
		#TODO: check owner exists

		# the user is not picking a location from their favourites,
		# then use the 'source_address' to create a new location.
		if cleaned_data['source'] is None:
			if cleaned_data['source_address'] == "":
				errors.append("Please choose a source address.")
			else:
				source_location = Location(
					owner=owner,
					address=cleaned_data['source_address']
				)
				source_location.put()
				cleaned_data['source'] = source_location

		# the user is not picking a location from their favourites,
		# then use the 'destination_address' to create a new location.
		if cleaned_data['destination'] is None:
			if cleaned_data['destination_address'] == "":
				errors.append("Please choose a destination address.")
			else:
				destination_location = Location(
					owner=owner,
					address=cleaned_data['destination_address']
				)
				destination_location.put()
				cleaned_data['destination'] = destination_location

		# validate times
		if cleaned_data['departure_time'] >= cleaned_data['arrival_time']:
			errors.append("Depature time must be before arrival time.")

		if errors:
			raise forms.ValidationError(errors)

		return cleaned_data

	class Meta:
		  model = Ride
		  exclude = ['owner', 'created']


