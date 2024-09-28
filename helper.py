# import necessary modules
import pandas as pd 
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import datetime as dt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Global function
def format_date_time(date):
    date = str(date)
    date_obj = dt.datetime.strptime(date, "%Y-%m-%dt%H:%M:%SZ")
    formatted_date = date_obj.strftime("%B %d, %Y, %I:%M %p")
    return formatted_date

# Popularity based recommendation
class PopularityBasedRecommendation():
    def __init__(self) -> None:
        courses = pd.read_csv("./static/courses.csv")
        self.popular_course = courses[(courses['num_subscribers']>12000) & (courses['num_reviews']>5000)]
        self.all_courses = courses
    
    def popular_courses(self, num_return):
        self.popular_course = self.popular_course.sort_values(by='num_subscribers', ascending=False, ignore_index=True)
        if num_return > self.popular_course.shape[0]:
            num_return = self.popular_course.shape[0]
        
        try:
            self.popular_course['image'] = self.popular_course['url'].apply(self.scrap_image)
        except Exception as e:
            return f"Unable to find image due to {e}"
        
        try:
            self.popular_course['published_timestamp'] = self.popular_course['published_timestamp'].apply(lambda x: format_date_time(x))
        except Exception as e:
            print(f"Date is in correct format")
            
        return self.popular_course.head(num_return)
    
    
    # Image Scrap from udemy site
    def scrap_image(self, c_url):
        response = requests.get(c_url)
        if response.status_code == 200:
            bs = BeautifulSoup(response.content, 'html.parser')
            spans = bs.find("span", class_="intro-asset--img-aspect--3gluH")
            if spans:
                first_image = spans.find("img")
                output = first_image.get("src")
                return output
        return "No Image Found"
    
    
    # get all courses
    def get_all_courses(self, num_return):
        num_return = int(num_return)
        try:
            self.all_courses['published_timestamp'] = self.all_courses['published_timestamp'].apply(lambda x: format_date_time(x))
        except Exception as e:
            print(f"Date is already formatted")
            
        return self.all_courses.head(num_return)
    
    # Find the details of a course
    def find_course_detail(self, c_id):
        c_id = int(c_id)
        c_detail = self.all_courses[self.all_courses['course_id']==c_id]
        url = c_detail['url'].values[0]
        c_detail['image'] = self.scrap_image(url)
        return c_detail
    
    
# Content based Recommendation
class ContentbasedRecommendation():
    def __init__(self) -> None:
        self.courses = pd.read_csv("./static/courses.csv")
        # initializing PorterStemmer
        self.stem = PorterStemmer()
        nltk.download("stopwords")
        self.stopwords = stopwords.words("english")
        
        self.courses['tags'] = self.courses['course_title']+" "+self.courses['subject']
        # preprocess the merged column
        self.courses['tags'] = self.courses['tags'].apply(self.preprocess)
        # vectorization
        self.tokenizer = TfidfVectorizer().fit_transform(self.courses['tags'])
        # finding similarity
        self.similarity = cosine_similarity(self.tokenizer)
        
    # preprocess the text
    def preprocess(self, text):
        stemmed_word = [self.stem.stem(word.lower()) for word in text.split(" ") if word.lower() not in self.stopwords]
        return " ".join(stemmed_word)
    
    # content based filtering function
    def content_based_filtering(self, c_id, n_recommend):
        n_recommend = int(n_recommend)
        c_id = int(c_id)
        
        course_index = self.courses[self.courses['course_id'] == c_id].index[0]
        distances = self.similarity[course_index]
        course_lists = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:n_recommend]
        
        output = []
        for course in course_lists:
            course_info = {
                "course_id": self.courses.iloc[course[0]]['course_id'],
                "title": self.courses.iloc[course[0]]['course_title'],
                "num_subscribers": self.courses.iloc[course[0]]['num_subscribers'],
                "num_reviews": self.courses.iloc[course[0]]['num_reviews'],
                "image": self.scrap_image(self.courses.iloc[course[0]]['url']),
            }
            output.append(course_info)
        return output
    
    # find image source
    def scrap_image(self, c_url):
        try:
            response = requests.get(c_url)
            if response.status_code == 200:
                bs = BeautifulSoup(response.content, 'html.parser')
                spans = bs.find("span", class_="intro-asset--img-aspect--3gluH")
                if spans:
                    first_image = spans.find("img")
                    output = first_image.get("src")
                    return output
            return "No image found"
        except:
            return "No Image found"