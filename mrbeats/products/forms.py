from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Genre

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "เช่น Hip-Hop / Pop / Jazz"
            }),
        }




class ProductForm(forms.ModelForm):
    file = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "form-file-input opacity-0 absolute inset-0"}))
    preview_file = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "form-file-input opacity-0 absolute inset-0"}))
    price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-input w-full p-2 rounded bg-gray-600 text-gray-100",
            "step": "0.01",
            "min": "0",
            "placeholder": "เช่น 19.99"
        })
    )

    class Meta:
        model = Product
        exclude = ("seller", "downloads")
        
        widgets = {
            "seller": forms.HiddenInput(),
            "title": forms.TextInput(attrs={
                "class": "form-input w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "placeholder": "ชื่อผลงาน"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-textarea w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "rows": 4,
                "placeholder": "คำอธิบายผลงาน"
            }),
            "bpm": forms.NumberInput(attrs={
                "class": "form-input w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "min": 1,
                "max": 2000,
                "placeholder": "เช่น 120"
            }),
            "music_key": forms.TextInput(attrs={
                "class": "form-input w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "placeholder": "เช่น C#m, F, Am"
            }),
            "genre": forms.Select(
                attrs={
                    "class": "w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                }),            
            "theme": forms.SelectMultiple(attrs={
                "class": "w-full p-3 rounded bg-gray-700 text-gray-100",
                "size": "5",
            }),
            "product_image": forms.FileInput(attrs={"class": "form-file-input opacity-0 absolute inset-0"}),
            "lyrics_text": forms.Textarea(attrs={
                "class": "form-textarea w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "row": 15,
                "placeholder": "เนื้อเพลงของคุณ...."
            }),
            "license_type": forms.Select(attrs={"class": "hidden"})
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise ValidationError("ราคาต้องไม่เป็นค่าติดลบ")
        return price

    def clean_bpm(self):
        bpm = self.cleaned_data.get("bpm")
        if bpm is None:
            return bpm
        if bpm <= 0 or bpm > 2000:
            raise ValidationError("BPM ต้องเป็นค่าบวกและเหมาะสม (1–2000)")
        return bpm

    def clean_file(self):
        f = self.cleaned_data.get("file")
        
        if not f:
            raise ValidationError("กรุณาเลือกไฟล์")
        
        max_mb = 50
        if f.size > max_mb * 1024 * 1024:
            raise ValidationError(f"ไฟล์หลักต้องไม่เกิน {max_mb} MB")
        return f

    def clean_preview_file(self):
        pf = self.cleaned_data.get("preview_file")
        if not pf:
            return pf
        max_mb = 50
        if pf.size > max_mb * 1024 * 1024:
            raise ValidationError(f"ไฟล์พรีวิวต้องไม่เกิน {max_mb} MB")
        return pf
    
    def clean(self):
        cleaned = super().clean()
        license_type = cleaned.get('license_type')
        price = cleaned.get('price')

        if license_type == 'royalty_free':
            cleaned['price'] = 0
        elif license_type in ('non_exclusive', 'exclusive'):
            if price in (None, ''):
                field_name = 'price'
                raise ValidationError({field_name: 'กรุณากรอกราคาเมื่อเลือก Non-exclusive หรือ Exclusive'})
            if price is not None and price < 0:
                raise ValidationError({'price': 'ราคาต้องมากกว่าหรือเท่ากับ 0'})
        else:
            raise ValidationError({'license_type': 'ค่าวิธีการขายไม่ถูกต้อง'})

        return cleaned
    
class LyricsForm(forms.ModelForm):
    file = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "form-file-input opacity-0 absolute inset-0"}))

    class Meta:
        model = Product
        exclude = ("seller", "downloads", "bpm", "music_key", "license_type", "preview_file")

        widgets = {
            "seller": forms.HiddenInput(),
            "title": forms.TextInput(attrs={
                "class": "form-input w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "placeholder": "ชื่อผลงาน"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-textarea w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "rows": 4,
                "placeholder": "คำอธิบายผลงาน"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-input w-full p-2 rounded bg-gray-600 text-gray-100",
                "step": "0.01",
                "min": "0",
                "placeholder": "เช่น 19.99"
            }),

            "genre": forms.Select(
                attrs={
                    "class": "w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                }),            
            "theme": forms.SelectMultiple(attrs={
                "class": "w-full p-3 rounded bg-gray-700 text-gray-100",
                "size": "5",
            }),
            "product_image": forms.FileInput(attrs={"class": "form-file-input opacity-0 absolute inset-0"}),
            "lyrics_text": forms.Textarea(attrs={
                "class": "form-textarea w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "row": 16,
                "placeholder": "เนื้อเพลงของคุณ...."
            }),
            "license_type": forms.Select(attrs={"class": "hidden"})
        }

        def clean_price(self):
            price = self.cleaned_data.get("price")
            if price is not None and price < 0:
                raise ValidationError("ราคาต้องไม่เป็นค่าติดลบ")
            return price

        def clean_file(self):
            f = self.cleaned_data.get("file")
            if not f:
                raise ValidationError("กรุณาเลือกไฟล์")
            max_mb = 50
            if f.size > max_mb * 1024 * 1024:
                raise ValidationError(f"ไฟล์หลักต้องไม่เกิน {max_mb} MB")
            return f


class EditProductForm(forms.ModelForm):
    file = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "form-file-input opacity-0 absolute inset-0"}))
    preview_file = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "form-file-input opacity-0 absolute inset-0"}))
    price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-input w-full p-2 rounded bg-gray-600 text-gray-100",
            "step": "0.01",
            "min": "0",
            "placeholder": "เช่น 19.99"
        })
    )

    class Meta:
        model = Product
        exclude = ("seller", "downloads")
        
        widgets = {
            "seller": forms.HiddenInput(),
            "title": forms.TextInput(attrs={
                "class": "form-input w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "placeholder": "ชื่อผลงาน"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-textarea w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "rows": 4,
                "placeholder": "คำอธิบายผลงาน"
            }),
            "bpm": forms.NumberInput(attrs={
                "class": "form-input w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "min": 1,
                "max": 2000,
                "placeholder": "เช่น 120"
            }),
            "music_key": forms.TextInput(attrs={
                "class": "form-input w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "placeholder": "เช่น C#m, F, Am"
            }),
            "genre": forms.Select(
                attrs={
                    "class": "w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                }),            
            "theme": forms.SelectMultiple(attrs={
                "class": "w-full p-3 rounded bg-gray-700 text-gray-100",
                "size": "5",
            }),
            "product_image": forms.FileInput(attrs={"class": "form-file-input opacity-0 absolute inset-0"}),
            "lyrics_text": forms.Textarea(attrs={
                "class": "form-textarea w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "row": 15,
                "placeholder": "เนื้อเพลงของคุณ...."
            }),
            "license_type": forms.Select(attrs={"class": "hidden"})
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise ValidationError("ราคาต้องไม่เป็นค่าติดลบ")
        return price

    def clean_bpm(self):
        bpm = self.cleaned_data.get("bpm")
        if bpm is None:
            return bpm
        if bpm <= 0 or bpm > 2000:
            raise ValidationError("BPM ต้องเป็นค่าบวกและเหมาะสม (1–2000)")
        return bpm

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if not f and self.instance and getattr(self.instance, 'file', None):
            return self.instance.file
        
        max_mb = 50
        if f.size > max_mb * 1024 * 1024:
            raise ValidationError(f"ไฟล์หลักต้องไม่เกิน {max_mb} MB")
        return f

    def clean_preview_file(self):
        pf = self.cleaned_data.get("preview_file")

        if not pf and self.instance and getattr(self.instance, 'preview_file', None):
            return self.instance.file
        
        max_mb = 50
        if pf.size > max_mb * 1024 * 1024:
            raise ValidationError(f"ไฟล์พรีวิวต้องไม่เกิน {max_mb} MB")
        return pf
    
    def clean(self):
        cleaned = super().clean()
        license_type = cleaned.get('license_type')
        price = cleaned.get('price')

        if license_type == 'royalty_free':
            cleaned['price'] = 0
        elif license_type in ('non_exclusive', 'exclusive'):
            if price in (None, ''):
                field_name = 'price'
                raise ValidationError({field_name: 'กรุณากรอกราคาเมื่อเลือก Non-exclusive หรือ Exclusive'})
            if price is not None and price < 0:
                raise ValidationError({'price': 'ราคาต้องมากกว่าหรือเท่ากับ 0'})
        else:
            raise ValidationError({'license_type': 'ค่าวิธีการขายไม่ถูกต้อง'})

        return cleaned

class EditLyricsForm(forms.ModelForm):
    file = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "form-file-input opacity-0 absolute inset-0"}))

    class Meta:
        model = Product
        exclude = ("seller", "downloads", "bpm", "music_key", "license_type", "preview_file")

        widgets = {
            "seller": forms.HiddenInput(),
            "title": forms.TextInput(attrs={
                "class": "form-input w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "placeholder": "ชื่อผลงาน"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-textarea w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "rows": 4,
                "placeholder": "คำอธิบายผลงาน"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-input w-full p-2 rounded bg-gray-600 text-gray-100",
                "step": "0.01",
                "min": "0",
                "placeholder": "เช่น 19.99"
            }),

            "genre": forms.Select(
                attrs={
                    "class": "w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                }),            
            "theme": forms.SelectMultiple(attrs={
                "class": "w-full p-3 rounded bg-gray-700 text-gray-100",
                "size": "5",
            }),
            "product_image": forms.ClearableFileInput(attrs={"class": "form-file-input opacity-0 absolute inset-0"}),
            "lyrics_text": forms.Textarea(attrs={
                "class": "form-textarea w-full p-3 rounded bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500",
                "row": 16,
                "placeholder": "เนื้อเพลงของคุณ...."
            }),
            "license_type": forms.Select(attrs={"class": "hidden"})
        }

        def clean_price(self):
            price = self.cleaned_data.get("price")
            if price is not None and price < 0:
                raise ValidationError("ราคาต้องไม่เป็นค่าติดลบ")
            return price

        def clean_file(self):
            f = self.cleaned_data.get("file")
            
            if not f and self.instance and getattr(self.instance, 'file', None):
                return self.instance.file
            
            max_mb = 50
            if f.size > max_mb * 1024 * 1024:
                raise ValidationError(f"ไฟล์หลักต้องไม่เกิน {max_mb} MB")
            return f
        