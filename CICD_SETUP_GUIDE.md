# CI/CD Pipeline Setup Guide for Telco Churn Prediction

## 🎯 Project Overview

This guide provides step-by-step instructions for setting up a complete CI/CD pipeline for the Telco Customer Churn Prediction project using Jenkins, GitHub Actions, Docker, and Flask.

## 👥 Team Structure

- **Student 1 (Admin)**: Can approve PRs, merge to master, receives notifications
- **Student 2 (Developer)**: Creates PRs, works on dev branch

## 🏗️ Pipeline Architecture

```
Dev Branch → Code Quality Check → Test Branch → Unit Tests → Master Branch → Jenkins → Docker Hub → Email Notification
```

## 📋 Step-by-Step Setup Instructions

### 1. GitHub Repository Setup

#### 1.1 Create Repository
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: Telco churn prediction project"

# Create branches
git checkout -b dev
git checkout -b test
git checkout master

# Push to GitHub (create repo on GitHub first)
git remote add origin https://github.com/yourusername/telco-churn-prediction.git
git push -u origin master
git push -u origin dev
git push -u origin test
```

#### 1.2 Configure Branch Protection Rules

1. Go to GitHub repository → Settings → Branches
2. **Dev Branch Protection:**
   - Require pull request reviews (1 reviewer)
   - Require status checks to pass
   - Restrict pushes to dev branch

3. **Test Branch Protection:**
   - Require pull request reviews (1 reviewer)
   - Require status checks to pass

4. **Master Branch Protection:**
   - Require pull request reviews (1 reviewer - Admin only)
   - Require status checks to pass
   - Restrict pushes to master branch

### 2. Jenkins Setup

#### 2.1 Install Jenkins
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install openjdk-11-jdk
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt update
sudo apt install jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

#### 2.2 Configure Jenkins

1. **Access Jenkins**: http://localhost:8080
2. **Install Required Plugins:**
   - GitHub Integration
   - Docker Pipeline
   - Email Extension
   - Blue Ocean (optional)

3. **Configure Global Tools:**
   - Go to Manage Jenkins → Global Tool Configuration
   - Configure Docker installation
   - Configure Git installation

4. **Create Docker Hub Credentials:**
   - Go to Manage Jenkins → Manage Credentials
   - Add new credentials (Username/Password)
   - ID: `docker-hub-credentials`

5. **Create Pipeline Job:**
   - New Item → Pipeline
   - Name: `telco-churn-pipeline`
   - Pipeline script from SCM
   - SCM: Git
   - Repository URL: Your GitHub repository
   - Script Path: `Jenkinsfile`

### 3. GitHub Actions Configuration

#### 3.1 Code Quality Workflow
- File: `.github/workflows/code_quality.yml`
- Triggers: Push to dev branch, PR to dev branch
- Actions: Install dependencies, run flake8, generate quality report

#### 3.2 Unit Tests Workflow
- File: `.github/workflows/unit_tests.yml`
- Triggers: Push to test branch, PR to test branch
- Actions: Install dependencies, run pytest, generate coverage report

### 4. Docker Configuration

#### 4.1 Dockerfile
- Base image: Python 3.9-slim
- Installs dependencies from requirements.txt
- Trains model during build
- Exposes port 5000
- Includes health check

#### 4.2 Build and Test Locally
```bash
# Build image
docker build -t telco-churn-prediction .

# Run container
docker run -p 5000:5000 telco-churn-prediction

# Test health endpoint
curl http://localhost:5000/health
```

### 5. Email Notifications Setup

#### 5.1 Configure SMTP in Jenkins
1. Go to Manage Jenkins → Configure System
2. Configure Extended E-mail Notification:
   - SMTP server: smtp.gmail.com (or your SMTP server)
   - Port: 587
   - Use SSL: Yes
   - Authentication: Username/Password
   - Default Recipients: admin@yourcompany.com

#### 5.2 Test Email Configuration
- Use Jenkins "Test configuration" button
- Send test email to verify setup

## 🔄 Workflow Process

### Development Workflow

1. **Developer pushes to dev branch:**
   ```bash
   git checkout dev
   git add .
   git commit -m "Add new feature"
   git push origin dev
   ```

2. **Code Quality Check triggers:**
   - GitHub Actions runs flake8
   - Code quality report generated
   - Status check must pass

3. **Create PR to test branch:**
   - Admin reviews and approves
   - PR merged to test branch

4. **Unit Tests trigger:**
   - GitHub Actions runs pytest
   - Test coverage report generated
   - Status check must pass

5. **Create PR to master branch:**
   - Admin reviews and approves
   - PR merged to master branch

6. **Jenkins Pipeline triggers:**
   - Builds Docker image
   - Runs tests
   - Pushes to Docker Hub
   - Deploys to staging
   - Sends email notification

## 🧪 Testing the Pipeline

### 1. Test Code Quality
```bash
# Make a change to app.py
echo "# Test comment" >> app.py
git add app.py
git commit -m "Test code quality check"
git push origin dev
```

### 2. Test Unit Tests
```bash
# Create a test PR to test branch
git checkout test
git merge dev
git push origin test
```

### 3. Test Full Pipeline
```bash
# Create a test PR to master branch
git checkout master
git merge test
git push origin master
```

## 📊 Monitoring and Logs

### GitHub Actions
- View workflow runs in GitHub → Actions tab
- Download artifacts (reports, logs)
- Check status checks on PRs

### Jenkins
- View build history in Jenkins dashboard
- Check console output for detailed logs
- Monitor email notifications

### Docker Hub
- Verify images are pushed successfully
- Check image tags and versions
- Monitor image size and layers

## 🚨 Troubleshooting

### Common Issues

1. **Code Quality Fails:**
   - Check flake8 output in GitHub Actions
   - Fix PEP 8 violations
   - Update .flake8 configuration if needed

2. **Unit Tests Fail:**
   - Check test output in GitHub Actions
   - Fix failing tests
   - Update test coverage requirements

3. **Jenkins Build Fails:**
   - Check Jenkins console output
   - Verify Docker Hub credentials
   - Check network connectivity

4. **Email Notifications Not Working:**
   - Verify SMTP configuration
   - Check Jenkins logs
   - Test email configuration

### Debug Commands

```bash
# Check Jenkins logs
sudo journalctl -u jenkins -f

# Check Docker status
docker ps
docker logs <container_name>

# Test GitHub Actions locally
act -l  # List available actions
act push  # Run push workflow locally
```

## 📈 Best Practices

1. **Code Quality:**
   - Use consistent code formatting
   - Add meaningful comments
   - Follow PEP 8 guidelines

2. **Testing:**
   - Write comprehensive unit tests
   - Maintain high test coverage
   - Test edge cases

3. **Documentation:**
   - Keep README updated
   - Document API endpoints
   - Maintain changelog

4. **Security:**
   - Use environment variables for secrets
   - Regularly update dependencies
   - Scan for vulnerabilities

## 🎉 Success Criteria

Your CI/CD pipeline is working correctly when:

- ✅ Code quality checks pass on dev branch pushes
- ✅ Unit tests pass on test branch pushes
- ✅ Jenkins builds and deploys on master branch pushes
- ✅ Docker images are pushed to Docker Hub
- ✅ Email notifications are sent to admin
- ✅ Application is accessible on staging environment

## 📞 Support

For issues or questions:
1. Check GitHub Actions logs
2. Review Jenkins console output
3. Consult this documentation
4. Contact your team members

---

**Happy Coding! 🚀**
