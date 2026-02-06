from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import compress_image, validate_pdf, validate_image
from .models import PDF, Roadmap, InterviewQuestion
from .supabase_client import supabase
import uuid

# signup
@api_view(["POST"])
def signup(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")

    if User.objects.filter(username=username).exists():
        return Response({"error": "User exists"}, status=400)

    User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    return Response({"message": "User created"})

# login
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view

@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if not user:
        return Response({"error": "Invalid credentials"}, status=401)

    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username,
        "is_admin": user.is_staff
    })




# ================= PDF =================
@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def pdfs(request):
    if request.method == "POST":
        try:
            title = request.POST.get("title")
            pdf_file = request.FILES.get("file")
            image = request.FILES.get("image")

            if not title or not pdf_file or not image:
                return Response({"error": "All fields required"}, status=400)

# ✅ ADD VALIDATION HERE
            try:
                validate_pdf(pdf_file)      # only PDF
                validate_image(image)       # only image
            except ValueError as e:
                return Response({"error": str(e)}, status=400)


            pdf_name = f"{uuid.uuid4()}-{pdf_file.name}"
            img_name = f"{uuid.uuid4()}-{image.name}"

            # Upload PDF
            supabase.storage.from_("pdfs").upload(
                path=pdf_name,
                file=pdf_file.read(),
                file_options={
                    "content-type": pdf_file.content_type,
                    "upsert": False
                }
            )

            # Upload Image
            compressed_image = compress_image(image)

            supabase.storage.from_("images").upload(
                path=img_name,
                file=compressed_image,
                file_options={
                    "content-type": "image/jpeg",
                    "upsert": False
                }
            )


            pdf_url = supabase.storage.from_("pdfs").get_public_url(pdf_name)
            img_url = supabase.storage.from_("images").get_public_url(img_name)

            # ⛔ PENDING BY DEFAULT
            PDF.objects.create(
                title=title,
                file_url=pdf_url,
                image_url=img_url,
                is_approved=request.user.is_staff

            )

            return Response({
                "message": "PDF uploaded successfully. Waiting for admin approval."
            })

        except Exception as e:
            print("PDF UPLOAD ERROR:", e)
            return Response({"error": str(e)}, status=500)

    # ✅ ONLY APPROVED PDFs
    data = PDF.objects.filter(is_approved=True).order_by("-created_at").values()
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pdf_download(request, pk):
    try:
        pdf = PDF.objects.get(id=pk, is_approved=True)
        pdf.download_count += 1
        pdf.save()

        return Response({
            "url": pdf.file_url,
            "download_count": pdf.download_count
        })
    except PDF.DoesNotExist:
        return Response({"error": "PDF not found"}, status=404)
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def increment_pdf_view(request, pk):
    pdf = PDF.objects.get(id=pk, is_approved=True)
    pdf.view_count += 1
    pdf.save()
    return Response({"views": pdf.view_count})




# ================= ROADMAP =================
@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def roadmaps(request):
    if request.method == "POST":
        try:
            title = request.POST.get("title")
            desc = request.POST.get("description")
            image = request.FILES.get("image")

            if not title or not desc or not image:
                return Response({"error": "All fields required"}, status=400)

            # ✅ ADD VALIDATION
            try:
                validate_image(image)
            except ValueError as e:
                return Response({"error": str(e)}, status=400)


            img_name = f"{uuid.uuid4()}-{image.name}"
            compressed_image = compress_image(image)

            supabase.storage.from_("images").upload(
                img_name,
                compressed_image,
                file_options={
                    "content-type": "image/jpeg",
                    "upsert": False
                }
            )
            img_url = supabase.storage.from_("images").get_public_url(img_name)

            # ⛔ PENDING BY DEFAULT
            Roadmap.objects.create(
                title=title,
                description=desc,
                image_url=img_url,
                is_approved=request.user.is_staff

            )

            return Response({
                "message": "Roadmap uploaded. Waiting for admin approval."
            })

        except Exception as e:
            print("ROADMAP UPLOAD ERROR:", e)
            return Response({"error": str(e)}, status=500)

    # ✅ ONLY APPROVED ROADMAPS
    data = Roadmap.objects.filter(is_approved=True).order_by("-created_at").values()
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def roadmap_download(request, pk):
    try:
        roadmap = Roadmap.objects.get(id=pk, is_approved=True)
        roadmap.download_count += 1
        roadmap.save()

        return Response({
            "url": roadmap.image_url,
            "download_count": roadmap.download_count
        })
    except Roadmap.DoesNotExist:
        return Response({"error": "Roadmap not found"}, status=404)
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def increment_roadmap_view(request, pk):
    roadmap = Roadmap.objects.get(id=pk, is_approved=True)
    roadmap.view_count += 1
    roadmap.save()
    return Response({"views": roadmap.view_count})



# ================= INTERVIEW QUESTIONS =================
@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def interview_questions(request):
    if request.method == "POST":
        try:
            company = request.POST.get("company")
            role = request.POST.get("role")
            pdf = request.FILES.get("file")

            if not company or not role or not pdf:
                return Response({"error": "All fields required"}, status=400)

            # ✅ ADD VALIDATION
            try:
                validate_pdf(pdf)
            except ValueError as e:
                return Response({"error": str(e)}, status=400)

            pdf_name = f"{uuid.uuid4()}-{pdf.name}"

            supabase.storage.from_("interview_pdfs").upload(
                path=pdf_name,
                file=pdf.read(),
                file_options={
                    "content-type": pdf.content_type,
                    "upsert": False
                }
            )

            pdf_url = supabase.storage.from_("interview_pdfs").get_public_url(pdf_name)

            # ⛔ PENDING BY DEFAULT
            InterviewQuestion.objects.create(
                company=company,
                role=role,
                pdf_url=pdf_url,
                is_approved=request.user.is_staff

            )

            return Response({
                "message": "Interview PDF uploaded. Waiting for admin approval."
            })

        except Exception as e:
            print("INTERVIEW UPLOAD ERROR:", e)
            return Response({"error": str(e)}, status=500)

    # ✅ ONLY APPROVED INTERVIEW QUESTIONS
    data = InterviewQuestion.objects.filter(
        is_approved=True
    ).order_by("company", "role").values()

    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def interview_download(request, pk):
    try:
        interview = InterviewQuestion.objects.get(id=pk, is_approved=True)
        interview.download_count += 1
        interview.save()

        return Response({
            "url": interview.pdf_url,
            "download_count": interview.download_count
        })
    except InterviewQuestion.DoesNotExist:
        return Response({"error": "Interview PDF not found"}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def increment_interview_view(request, pk):
    interview = InterviewQuestion.objects.get(id=pk, is_approved=True)
    interview.view_count += 1
    interview.save()
    return Response({"views": interview.view_count})





# ================= ADMIN =================

@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_pdfs(request):
    try:
        data = PDF.objects.filter(is_approved=False).values()
        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_roadmaps(request):
    try:
        data = Roadmap.objects.filter(is_approved=False).values()
        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_interviews(request):
    try:
        data = InterviewQuestion.objects.filter(is_approved=False).values()
        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def approve_pdf(request, pk):
    try:
        pdf = PDF.objects.get(id=pk)
        pdf.is_approved = True
        pdf.save()
        return Response({"message": "PDF approved"})
    except PDF.DoesNotExist:
        return Response({"error": "PDF not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def approve_roadmap(request, pk):
    try:
        roadmap = Roadmap.objects.get(id=pk)
        roadmap.is_approved = True
        roadmap.save()
        return Response({"message": "Roadmap approved"})
    except Roadmap.DoesNotExist:
        return Response({"error": "Roadmap not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def approve_interview(request, pk):
    try:
        interview = InterviewQuestion.objects.get(id=pk)
        interview.is_approved = True
        interview.save()
        return Response({"message": "Interview approved"})
    except InterviewQuestion.DoesNotExist:
        return Response({"error": "Interview not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# ---------- REJECT ----------
@api_view(["POST"])
@permission_classes([IsAdminUser])
def reject_pdf(request, pk):
    PDF.objects.filter(id=pk).delete()
    return Response({"message": "PDF rejected"})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def reject_roadmap(request, pk):
    Roadmap.objects.filter(id=pk).delete()
    return Response({"message": "Roadmap rejected"})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def reject_interview(request, pk):
    InterviewQuestion.objects.filter(id=pk).delete()
    return Response({"message": "Interview rejected"})
