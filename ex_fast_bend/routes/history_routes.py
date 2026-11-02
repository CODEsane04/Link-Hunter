from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from bson import ObjectId

from database import history_collection
from utils.deps import get_current_user

#for a user, we will get their history & return it

#define the prefix
router = APIRouter(prefix="/history")

@router.get("/get_history")
async def get_user_history(current_user : dict = Depends(get_current_user)) :

    try :

        cursor = history_collection.find(
            {"email": current_user["email"]}
        ).sort("created_at", -1).limit(20)
        user_history_list = await cursor.to_list(length=20)

        #FastAPI cannot convert raw ObjectId types to JSON—it will crash with: ValueError: ObjectId is not JSON serializable.
        for item in user_history_list :
            item["_id"] = str(item["_id"])
            
        return user_history_list
    except Exception as e :
        raise HTTPException (
            status_code=400,
            detail=f"failed to get user history : {e}"
        )

@router.delete("/delete_history/{history_id}")
async def delete_user_history(history_id : str, current_user : dict = Depends(get_current_user)) :

    try :
        result = await history_collection.delete_one({"_id" : ObjectId(history_id), "email" : current_user["email"]})
    except Exception as e :
        raise HTTPException(
            status_code=400,
            detail=f"could not delete item {e}"
        )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="History item not found")
    return {
            "message" : "successfully deleted entry from DB"
        }