from flask import Flask, render_template
from helper import PopularityBasedRecommendation
from helper import ContentbasedRecommendation


# initialize flask application
application = Flask(__name__)


# class initialization
popular_course_reco = PopularityBasedRecommendation()
content_based_reco = ContentbasedRecommendation()

# Home Page
@application.route("/", methods=["GET"])
def home_page():
    all_courses = popular_course_reco.get_all_courses(50)
    return render_template("index.html", courses = all_courses)

# Popularity based recommendation
@application.route("/popular", methods=["GET"])
def popular_courses():
    popular_courses_list = popular_course_reco.popular_courses(5)
    print(popular_courses_list)
    return render_template("popular.html", popular_courses_list=popular_courses_list)

# Content based recommendation
@application.route("/courses/<id>", methods=["GET","POST"])
def get_content_based_reommendation(id):
    course_detail = popular_course_reco.find_course_detail(id)
    reco_course = content_based_reco.content_based_filtering(id, n_recommend=6)
    
    return render_template("course_detail.html", c_detail=course_detail, reco_course=reco_course)


# Run the application
if __name__ == "__main__":
    application.run(host="0.0.0.0", debug=True)
