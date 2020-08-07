from django.shortcuts import render
from .models import CourseOrg, CityDict
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
# 处理课程机构列表的view
from django.views.generic.base import View


class OrgView(View):
    def get(self,request):
        all_orgs = CourseOrg.objects.all()
        # 热门机构 取三个
        hot_orgs = all_orgs.order_by('-click_nums')[:3]
        # 城市
        all_city = CityDict.objects.all()

        # 以城市为筛选
        city_id = request.GET.get('city', "")
        if city_id:
            #
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 以机构类别为筛选
        category = request.GET.get('ct', "")
        if category:
            #
            all_orgs = all_orgs.filter(category=category)

        # 排序方式 有学习人数 机构课程数
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        # 总共有多少家机构使用count进行统计
        org_nums = all_orgs.count()
        # 分页
        page = request.GET.get('page', 1)
        p = Paginator(all_orgs, 4, request=request) # 每页显示五个
        orgs = p.page(page) # orgs代表第page页的内容

        return render(request, "org-list.html", {
            "all_orgs": orgs,
            "all_city": all_city,
            "org_nums": org_nums,
            "city_id": city_id,
            "category": category,
            "hot_orgs": hot_orgs,
            "sort": sort,
        })
