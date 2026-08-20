import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  email = '';
  password = '';
  errorMessage = '';

  constructor(
    private http: HttpClient,
    private router: Router
  ) { }

  login() {
    this.errorMessage = '';

    const body = {
      email: this.email,
      password: this.password
    };

    this.http.post<any>(
      'http://127.0.0.1:8000/auth/login',
      body
    ).subscribe({
      next: (response) => {
        localStorage.setItem(
          'access_token',
          response.access_token
        );

        this.router.navigate(['/dashboard']);
      },

      error: () => {
        this.errorMessage = 'Correo o contraseña incorrectos';
      }
    });
  }
}